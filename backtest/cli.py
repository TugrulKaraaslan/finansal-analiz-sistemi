from __future__ import annotations

import argparse
from pathlib import Path

import click
import pandas as pd
from datetime import timedelta
from loguru import logger

from io_filters import load_filters_csv
from utils.paths import resolve_path
from .io.preflight import preflight

from .backtester import run_1g_returns
from .benchmark import BenchmarkLoader
from .calendars import (
    add_next_close,
    add_next_close_calendar,
    build_trading_days,
    load_holidays_csv,
)
from .config import load_config
from .data_loader import apply_corporate_actions, read_excels_long
from .crossovers import generate_crossovers
from .indicators import compute_indicators
from .normalizer import normalize
from .reporter import write_reports
from .screener import run_screener
from .utils.names import set_name_normalization
from .validator import dataset_summary, quality_warnings
from .logging_utils import setup_logger, Timer
from .filters_compile import compile_filters
from .filters_cleanup import clean_filters
from .filters_io import load_filters, save_csv
from backtest.validation import validate_filters


@click.group()
@click.option("--log-level", default="INFO", help="Log level: DEBUG/INFO/WARN/ERROR")
@click.option("--run-id", default=None, help="Custom run id for log filename")
@click.pass_context
def cli(ctx, log_level: str, run_id: str | None):
    logfile = setup_logger(run_id=run_id, level=log_level)
    ctx.ensure_object(dict)
    ctx.obj["logfile"] = logfile
    logger.info("CLI initialized")


def _run_scan(cfg, *, per_day_output: bool = False, csv_also: bool = True) -> None:
    """Common execution for scan commands.

    The filters CSV must provide ``FilterCode`` and ``PythonQuery`` columns and
    may include an optional ``Group`` column.
    """
    try:
        with Timer("yükleme"):
            df = read_excels_long(cfg)
    except (FileNotFoundError, RuntimeError, ImportError) as exc:
        logger.error(str(exc))
        raise click.ClickException(str(exc))
    df = apply_corporate_actions(df, getattr(cfg.data, "corporate_actions_csv", None))
    df = normalize(df)
    if cfg.calendar.tplus1_mode == "calendar":
        holidays = None
        if cfg.calendar.holidays_source == "csv" and cfg.calendar.holidays_csv_path:
            holidays = load_holidays_csv(cfg.calendar.holidays_csv_path)
        tdays = build_trading_days(df, holidays)
        df = add_next_close_calendar(df, tdays)
    else:
        tdays = None
        df = add_next_close(df)
    logger.info("Göstergeler hesaplanıyor...")
    with Timer("compute_indicators"):
        df_ind = compute_indicators(
            df, cfg.indicators.params, engine=cfg.indicators.engine
        )
    df_ind = generate_crossovers(df_ind)
    logger.info("Filtreler hazırlanıyor...")
    src = Path(cfg.data.filters_csv)
    load_path = src
    try:
        with Timer("filtre"):
            if src.exists():
                compile_filters(src, src.with_name("filters_compiled.csv"))
                load_path = src.with_name("filters_compiled.csv")
            filters_df = load_filters_csv(load_path)
    except FileNotFoundError as exc:
        logger.error(str(exc))
        raise click.ClickException(str(exc))
    if filters_df.empty:
        msg = "Filtre CSV boş veya bulunamadı, işlem yapılmadı."
        logger.error(msg)
        raise click.ClickException(msg)

    all_days = sorted(pd.to_datetime(df_ind["date"]).dt.normalize().unique())
    if cfg.project.run_mode == "single" and cfg.project.single_date:
        day = pd.to_datetime(cfg.project.single_date).normalize()
        days = [day]
    else:
        if not all_days:
            msg = "Taranacak tarih bulunamadı, veri seti boş."
            logger.error(msg)
            raise click.ClickException(msg)
        start = (
            pd.to_datetime(cfg.project.start_date).normalize()
            if cfg.project.start_date
            else all_days[0]
        )
        end = (
            pd.to_datetime(cfg.project.end_date).normalize()
            if cfg.project.end_date
            else all_days[-1]
        )
        if start > end:
            start, end = end, start
        days = [d for d in all_days if start <= d <= end]
    all_trades = []
    if len(days) > 1:
        logger.info(f"{len(days)} gün taranacak...")
    with Timer("getiri"):
        for d in days:
            with Timer(f"run_screener {d.date()}"):
                sigs = run_screener(
                    df_ind,
                    filters_df,
                    d,
                    stop_on_filter_error=getattr(
                        cfg.project, "stop_on_filter_error", False
                    ),
                    raise_on_error=cfg.project.raise_on_error,
                )
            with Timer(f"run_1g_returns {d.date()}"):
                trades = run_1g_returns(
                    df_ind,
                    sigs,
                    cfg.project.holding_period,
                    cfg.project.transaction_cost,
                    trading_days=tdays,
                )
            all_trades.append(trades)
    trades_all = (
        pd.concat(all_trades, ignore_index=True)
        if all_trades
        else pd.DataFrame(
            columns=[
                "FilterCode",
                "Group",
                "Symbol",
                "Date",
                "EntryClose",
                "ExitClose",
                "Side",
                "ReturnPct",
                "Win",
            ]
        )
    )
    if not trades_all.empty:
        pivot = (
            trades_all.groupby(["FilterCode", "Side", "Date"])["ReturnPct"]
            .mean()
            .unstack(fill_value=float("nan"))
        )
        pivot = pivot.reindex(columns=days)
        pivot["Ortalama"] = pivot.mean(axis=1)
        winrate = (
            trades_all.groupby(["FilterCode", "Side", "Date"])["Win"]
            .mean()
            .unstack(fill_value=float("nan"))
        )
        winrate = winrate.reindex(columns=days)
        winrate["Ortalama"] = winrate.mean(axis=1)
        group_cols = ["FilterCode"]
        if "Side" in trades_all.columns:
            group_cols.append("Side")
        valid_trades = trades_all[trades_all["ReturnPct"].notna()]
        trade_counts = valid_trades.groupby(group_cols)["Symbol"].count()
        pivot = pivot.assign(TradeCount=trade_counts)
    else:
        pivot = pd.DataFrame(columns=[*days, "Ortalama", "TradeCount"])
        winrate = pd.DataFrame(columns=[*days, "Ortalama"])
    bm_cfg = getattr(cfg, "benchmark", None)
    xu100_pct = None
    if bm_cfg is not None:
        cfg_dict = (
            bm_cfg.model_dump()
            if hasattr(bm_cfg, "model_dump")
            else bm_cfg.dict()
            if hasattr(bm_cfg, "dict")
            else vars(bm_cfg)
            if hasattr(bm_cfg, "__dict__")
            else bm_cfg
        )
        try:
            bench_df = BenchmarkLoader(cfg_dict).load()
        except (FileNotFoundError, ValueError) as exc:
            logger.error(str(exc))
            raise click.ClickException(str(exc))
        if bench_df is not None:
            s = bench_df.set_index("date")["close"].pct_change() * 100.0
            xu100_pct = {pd.Timestamp(d): float(v) for d, v in s.dropna().items()}
    out_dir = resolve_path(cfg.project.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    if per_day_output:
        out_xlsx = out_dir
        out_csv_dir = None
    elif len(days) == 1:
        out_xlsx = out_dir / f"SCAN_{days[0].date()}.xlsx"
        out_csv_dir = None
    else:
        out_xlsx = out_dir / f"{days[0].date()}_{days[-1].date()}_1G_BIST100.xlsx"
        out_csv_dir = out_dir / "csv"
    logger.info("Raporlar yazılıyor...")
    val_sum = dataset_summary(df)
    val_iss = quality_warnings(df)
    with Timer("rapor"):
        outputs = write_reports(
            trades_all,
            days,
            pivot,
            xu100_pct,
            out_xlsx=out_xlsx,
            out_csv_dir=out_csv_dir,
            validation_summary=val_sum,
            validation_issues=val_iss,
            summary_winrate=winrate,
            daily_sheet_prefix=cfg.report.daily_sheet_prefix,
            summary_sheet_name=cfg.report.summary_sheet_name,
            percent_fmt=cfg.report.percent_format,
            with_bist_ratio_summary=getattr(
                cfg.report, "with_bist_ratio_summary", False
            ),
            per_day_output=per_day_output,
            csv_also=csv_also,
        )
    logger.info(f"Bitti. Çıktı: {outputs.get('excel')}")
    if outputs.get("csv"):
        logger.info(f"CSV klasörü: {outputs['csv'][0].parent}")
    with Timer("cleanup"):
        if load_path.name == "filters_compiled.csv" and load_path.exists():
            load_path.unlink(missing_ok=True)


@cli.command("scan-range")
@click.option(
    "--config",
    "config_path",
    default="config_scan.yml",
    show_default=True,
    help=("YAML config yolu (CLI argümanı > varsayılan). " "Mutlak veya göreli yol"),
)
@click.option("--start", "start_date", required=False, default=None, help="YYYY-MM-DD")
@click.option("--end", "end_date", required=False, default=None, help="YYYY-MM-DD")
@click.option("--holding-period", default=None, type=int)
@click.option("--transaction-cost", default=None, type=float)
@click.option(
    "--name-normalization",
    "name_normalization",
    type=click.Choice(["off", "smart", "strict"]),
    default="smart",
)
@click.option(
    "--per-day-output",
    is_flag=True,
    default=False,
    help="Günlük dosya çıktısı",
)
@click.option("--csv-also/--no-csv", default=True, help="CSV de yaz")
@click.option(
    "--no-preflight",
    is_flag=True,
    default=False,
    help="Preflight kontrolünü atla (veya config'te preflight: false)",
)
@click.option(
    "--case-insensitive",
    is_flag=True,
    default=False,
    help="Dosya adlarında küçük/büyük harf farkını yok say",
)
@click.option(
    "--filters-csv",
    "filters_csv",
    default=None,
    help=(
        "Filters CSV yolu. Öncelik: CLI argümanı > YAML config > "
        "varsayılan 'filters.csv'. Mutlak veya göreli yol"
    ),
)
@click.option(
    "--reports-dir",
    default="raporlar/",
    help="Directory for generated reports",
)
@click.option(
    "--report-alias",
    is_flag=True,
    default=False,
    help="Generate alias mismatch report",
)
def scan_range(
    config_path,
    start_date,
    end_date,
    holding_period,
    transaction_cost,
    name_normalization="smart",
    per_day_output=False,
    csv_also=True,
    *,
    no_preflight=False,
    case_insensitive=False,
    filters_csv=None,
    reports_dir="raporlar/",
    report_alias=False,
):
    set_name_normalization(name_normalization)
    try:
        cfg_path = Path(config_path).expanduser().resolve()
        cfg = load_config(cfg_path)
    except Exception as exc:  # kullanıcı dostu mesaj
        logger.error(str(exc))
        raise click.ClickException(str(exc))
    fc = filters_csv or getattr(cfg.data, "filters_csv", None) or "filters.csv"
    cfg.data.filters_csv = str(Path(fc).expanduser().resolve())
    if report_alias:
        filters_df = load_filters(cfg.data.filters_csv)
        df_clean, report_df = clean_filters(filters_df)
        reports_dir_path = Path(reports_dir)
        reports_dir_path.mkdir(parents=True, exist_ok=True)
        save_csv(report_df, reports_dir_path / "alias_uyumsuzluklar.csv")
        intraday_df = report_df[report_df["status"] == "intraday_removed"]
        if not intraday_df.empty:
            save_csv(intraday_df, reports_dir_path / "filters_intraday_disabled.csv")
        aliased = (report_df["status"] == "aliased").sum()
        removed = (report_df["status"] == "intraday_removed").sum()
        click.echo(
            f"alias matched: {aliased}, intraday removed: {removed}",
            err=False,
        )
        # Use cleaned filters for subsequent processing
        save_csv(df_clean, cfg.data.filters_csv)
    if start_date:
        cfg.project.start_date = start_date
    if end_date:
        cfg.project.end_date = end_date
    if holding_period is not None:
        cfg.project.holding_period = holding_period
    if transaction_cost is not None:
        cfg.project.transaction_cost = transaction_cost
    cfg.project.run_mode = "range"
    if case_insensitive:
        cfg.data.case_sensitive = False
    skip_preflight = no_preflight or not getattr(cfg, "preflight", True)
    if not skip_preflight and cfg.project.start_date and cfg.project.end_date:
        start = pd.to_datetime(cfg.project.start_date).date()
        end = pd.to_datetime(cfg.project.end_date).date()
        days = [start + timedelta(days=i) for i in range((end - start).days + 1)]
        rep = preflight(
            cfg.data.excel_dir,
            days,
            cfg.data.filename_pattern,
            date_format=cfg.data.date_format,
            case_sensitive=cfg.data.case_sensitive,
        )
        if rep.errors:
            raise click.ClickException("; ".join(rep.errors))
        for msg in rep.warnings:
            logger.warning(msg)
        for msg in rep.suggestions:
            logger.info(msg)
    try:
        with Timer("toplam") as t:
            _run_scan(cfg, per_day_output=per_day_output, csv_also=csv_also)
        logger.info("Toplam süre: {} ms", t.elapsed_ms)
    except Exception:
        logger.exception("scan_range failed")
        raise


@cli.command("scan-day")
@click.option(
    "--config",
    "config_path",
    default="config_scan.yml",
    show_default=True,
    help=("YAML config yolu (CLI argümanı > varsayılan). " "Mutlak veya göreli yol"),
)
@click.option("--date", "date_str", required=True, help="YYYY-MM-DD")
@click.option("--holding-period", default=None, type=int)
@click.option("--transaction-cost", default=None, type=float)
@click.option(
    "--filters-csv",
    "filters_csv",
    default=None,
    help=(
        "Filters CSV yolu. Öncelik: CLI argümanı > YAML config > "
        "varsayılan 'filters.csv'. Mutlak veya göreli yol"
    ),
)
@click.option(
    "--no-preflight",
    is_flag=True,
    default=False,
    help="Preflight kontrolünü atla (veya config'te preflight: false)",
)
@click.option(
    "--case-insensitive",
    is_flag=True,
    default=False,
    help="Dosya adlarında küçük/büyük harf farkını yok say",
)
def scan_day(
    config_path,
    date_str,
    holding_period,
    transaction_cost,
    *,
    filters_csv=None,
    no_preflight=False,
    case_insensitive=False,
):
    try:
        cfg_path = Path(config_path).expanduser().resolve()
        cfg = load_config(cfg_path)
    except Exception as exc:  # kullanıcı dostu mesaj
        logger.error(str(exc))
        raise click.ClickException(str(exc))
    fc = filters_csv or getattr(cfg.data, "filters_csv", None) or "filters.csv"
    cfg.data.filters_csv = str(Path(fc).expanduser().resolve())
    cfg.project.single_date = date_str
    cfg.project.run_mode = "single"
    if holding_period is not None:
        cfg.project.holding_period = holding_period
    if transaction_cost is not None:
        cfg.project.transaction_cost = transaction_cost
    if case_insensitive:
        cfg.data.case_sensitive = False
    skip_preflight = no_preflight or not getattr(cfg, "preflight", True)
    if not skip_preflight:
        d = pd.to_datetime(date_str).date()
        rep = preflight(
            cfg.data.excel_dir,
            [d],
            cfg.data.filename_pattern,
            date_format=cfg.data.date_format,
            case_sensitive=cfg.data.case_sensitive,
        )
        if rep.errors:
            raise click.ClickException("; ".join(rep.errors))
        for msg in rep.warnings:
            logger.warning(msg)
        for msg in rep.suggestions:
            logger.info(msg)
    try:
        with Timer("toplam") as t:
            _run_scan(cfg)
        logger.info("Toplam süre: {} ms", t.elapsed_ms)
    except Exception:
        logger.exception("scan_day failed")
        raise


if __name__ == "__main__":
    import sys

    if "--dry-run" in sys.argv:
        parser = argparse.ArgumentParser()
        parser.add_argument("--filters", type=str, required=True)
        parser.add_argument("--alias", type=str, default=None)
        parser.add_argument("--dry-run", action="store_true")
        args = parser.parse_args()
        rep = validate_filters(args.filters, args.alias)
        if rep.ok():
            print("✅ Uyum Tam")
            sys.exit(0)
        else:
            for err in rep.errors:
                print(f"❌ Satır {err['row']} | {err['code']} | {err['msg']}")
            for warn in rep.warnings:
                print(f"⚠️ Satır {warn['row']} | {warn['code']} | {warn['msg']}")
            sys.exit(1)
    else:
        try:
            cli()
        except SystemExit as exc:
            code = getattr(exc, "code", 1)
            if code == 0:
                logger.info("Program başarıyla tamamlandı.")
            else:
                logger.error("Program %s kodu ile hata vererek sonlandı.", code)
            raise
