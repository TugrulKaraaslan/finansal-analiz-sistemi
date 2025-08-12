# DÜZENLENDİ – SYNTAX TEMİZLİĞİ
from __future__ import annotations

import click
import pandas as pd
from loguru import logger

from io_filters import load_filters_csv
from utils.paths import resolve_path

from .backtester import run_1g_returns
from .benchmark import load_xu100_pct
from .calendars import (
    add_next_close,
    add_next_close_calendar,
    build_trading_days,
    load_holidays_csv,
)
from .config import load_config
from .data_loader import apply_corporate_actions, read_excels_long
from .indicators import compute_indicators
from .normalizer import normalize
from .reporter import write_reports
from .screener import run_screener
from .utils import info, set_name_normalization
from .validator import dataset_summary, quality_warnings


@click.group()
def cli():
    pass


def _run_scan(cfg) -> None:
    """Common execution for scan commands.

    The filters CSV must provide ``FilterCode`` and ``PythonQuery`` columns and
    may include an optional ``Group`` column.
    """
    info("Excelleri okuyor...")
    try:
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
    info("Göstergeler hesaplanıyor...")
    df_ind = compute_indicators(
        df, cfg.indicators.params, engine=cfg.indicators.engine
    )
    info("Filtre CSV okunuyor...")
    try:
        filters_df = load_filters_csv(cfg.data.filters_csv)
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
        info(f"{len(days)} gün taranacak...")
    for d in days:
        sigs = run_screener(
            df_ind,
            filters_df,
            d,
            strict=True,
            raise_on_error=cfg.project.raise_on_error,
        )
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
            trades_all.groupby(["FilterCode", "Side", "Date"])["ReturnPct"].mean().unstack(
                fill_value=float("nan")
            )
        )
        pivot = pivot.reindex(columns=days)
        pivot["Ortalama"] = pivot.mean(axis=1)
        winrate = (
            trades_all.groupby(["FilterCode", "Side", "Date"])["Win"].mean().unstack(
                fill_value=float("nan")
            )
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
    xu100_pct = None
    if cfg.benchmark.xu100_source == "csv" and cfg.benchmark.xu100_csv_path:
        s = load_xu100_pct(cfg.benchmark.xu100_csv_path)
        xu100_pct = {
            d: float(s.get(d, float("nan")))
            for d in pivot.columns
            if d not in {"Ortalama", "TradeCount"}
        }
    out_dir = resolve_path(cfg.project.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    if len(days) == 1:
        out_xlsx = out_dir / f"SCAN_{days[0].date()}.xlsx"
        out_csv_dir = None
    else:
        out_xlsx = out_dir / f"{days[0].date()}_{days[-1].date()}_1G_BIST100.xlsx"
        out_csv_dir = out_dir / "csv"
    info("Raporlar yazılıyor...")
    val_sum = dataset_summary(df)
    val_iss = quality_warnings(df)
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
    )
    info(f"Bitti. Çıktı: {outputs.get('excel')}")
    if outputs.get("csv"):
        info(f"CSV klasörü: {outputs['csv'][0].parent}")


@cli.command("scan-range")
@click.option("--config", "config_path", required=True, help="YAML config yolu")
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
def scan_range(
    config_path,
    start_date,
    end_date,
    holding_period,
    transaction_cost,
    name_normalization="smart",
):
    set_name_normalization(name_normalization)
    cfg = load_config(config_path)
    if start_date:
        cfg.project.start_date = start_date
    if end_date:
        cfg.project.end_date = end_date
    if holding_period is not None:
        cfg.project.holding_period = holding_period
    if transaction_cost is not None:
        cfg.project.transaction_cost = transaction_cost
    cfg.project.run_mode = "range"
    _run_scan(cfg)


@cli.command("scan-day")
@click.option("--config", "config_path", required=True)
@click.option("--date", "date_str", required=True, help="YYYY-MM-DD")
@click.option("--holding-period", default=None, type=int)
@click.option("--transaction-cost", default=None, type=float)
def scan_day(config_path, date_str, holding_period, transaction_cost):
    cfg = load_config(config_path)
    cfg.project.single_date = date_str
    cfg.project.run_mode = "single"
    if holding_period is not None:
        cfg.project.holding_period = holding_period
    if transaction_cost is not None:
        cfg.project.transaction_cost = transaction_cost
    _run_scan(cfg)


if __name__ == "__main__":
    cli()
