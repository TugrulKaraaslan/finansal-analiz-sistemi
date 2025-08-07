# DÜZENLENDİ – SYNTAX TEMİZLİĞİ
from __future__ import annotations

import click
import pandas as pd

from io_filters import load_filters_csv
from utils.paths import resolve_path

from .backtester import run_1g_returns
from .benchmark import load_xu100_pct
from .calendars import (add_next_close, add_next_close_calendar,
                        build_trading_days, load_holidays_csv)
from .config import load_config
from .data_loader import read_excels_long
from .indicators import compute_indicators
from .normalizer import normalize
from .reporter import write_reports
from .screener import run_screener
from .utils import info
from .validator import dataset_summary, quality_warnings


@click.group()
def cli():
    pass


@cli.command("scan-range")
@click.option("--config", "config_path", required=True, help="YAML config yolu")
@click.option("--start", "start_date", required=False, default=None, help="YYYY-MM-DD")
@click.option("--end", "end_date", required=False, default=None, help="YYYY-MM-DD")
def scan_range(config_path, start_date, end_date):
    cfg = load_config(config_path)
    if start_date:
        cfg.project.start_date = start_date
    if end_date:
        cfg.project.end_date = end_date
    info("Excelleri okuyor...")
    try:
        df = read_excels_long(cfg)
    except (FileNotFoundError, RuntimeError) as exc:
        info(str(exc))
        return
    df = normalize(df)
    if cfg.calendar.tplus1_mode == "calendar":
        holidays = None
        if cfg.calendar.holidays_source == "csv" and cfg.calendar.holidays_csv_path:
            holidays = load_holidays_csv(cfg.calendar.holidays_csv_path)
        tdays = build_trading_days(df, holidays)
        df = add_next_close_calendar(df, tdays)
    else:
        df = add_next_close(df)
    info("Göstergeler hesaplanıyor...")
    df_ind = compute_indicators(df, cfg.indicators.params)
    info("Filtre CSV okunuyor...")
    try:
        filters_df = load_filters_csv(cfg.data.filters_csv)
    except FileNotFoundError as exc:
        info(str(exc))
        filters_df = pd.DataFrame(columns=["FilterCode", "PythonQuery"])
    if filters_df.empty:
        info("Filtre CSV boş veya bulunamadı, işlem yapılmadı.")
        return
    all_days = sorted(pd.to_datetime(df_ind["date"]).dt.normalize().unique())
    if not all_days:
        info("Taranacak tarih bulunamadı, veri seti boş.")  # LOJİK HATASI DÜZELTİLDİ
        return  # Liste boşsa başlangıç/bitiş alınamaz
    start = (
        pd.to_datetime(cfg.project.start_date).normalize()
        if cfg.project.start_date
        else all_days[0]
    )
    end = (
        pd.to_datetime(cfg.project.end_date).normalize()
        if cfg.project.end_date
        else all_days[len(all_days) - 1]  # Negatif indeks yerine açık indeks
    )  # LOJİK HATASI DÜZELTİLDİ
    if start > end:
        start, end = end, start  # LOJİK HATASI DÜZELTİLDİ
    days = [d for d in all_days if start <= d <= end]
    all_trades = []
    info(f"{len(days)} gün taranacak...")
    for d in days:
        sigs = run_screener(df_ind, filters_df, d)
        trades = run_1g_returns(df_ind, sigs)
        all_trades.append(trades)
    trades_all = (
        pd.concat(all_trades, ignore_index=True)
        if all_trades
        else pd.DataFrame(
            columns=[
                "FilterCode",
                "Symbol",
                "Date",
                "EntryClose",
                "ExitClose",
                "ReturnPct",
                "Win",
            ]
        )
    )
    if not trades_all.empty:
        pivot = (
            trades_all.groupby(["FilterCode", "Date"])["ReturnPct"]
            .mean()
            .unstack(fill_value=float("nan"))
        )
        pivot["Ortalama"] = pivot.mean(axis=1)
        winrate = (
            trades_all.groupby(["FilterCode", "Date"])["Win"]
            .mean()
            .unstack(fill_value=float("nan"))
        )
        winrate["Ortalama"] = winrate.mean(axis=1)
    else:
        pivot = pd.DataFrame()
        winrate = pd.DataFrame()  # TİP DÜZELTİLDİ
    xu100_pct = None
    if cfg.benchmark.xu100_source == "csv" and cfg.benchmark.xu100_csv_path:
        s = load_xu100_pct(cfg.benchmark.xu100_csv_path)
        xu100_pct = {
            d: float(s.get(d, float("nan"))) for d in pivot.columns if d != "Ortalama"
        }
    out_dir = resolve_path(cfg.project.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_xlsx = out_dir / f"{start.date()}_{end.date()}_1G_BIST100.xlsx"
    out_csv_dir = out_dir / "csv"
    info("Raporlar yazılıyor...")
    val_sum = dataset_summary(df)
    val_iss = quality_warnings(df)
    write_reports(
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
    info(f"Bitti. Çıktı: {out_xlsx}")


@cli.command("scan-day")
@click.option("--config", "config_path", required=True)
@click.option("--date", "date_str", required=True, help="YYYY-MM-DD")
def scan_day(config_path, date_str):
    cfg = load_config(config_path)
    cfg.project.single_date = date_str
    cfg.project.run_mode = "single"
    info("Excelleri okuyor...")
    try:
        df = read_excels_long(cfg)
    except (FileNotFoundError, RuntimeError) as exc:
        info(str(exc))
        return
    df = normalize(df)
    if cfg.calendar.tplus1_mode == "calendar":
        holidays = None
        if cfg.calendar.holidays_source == "csv" and cfg.calendar.holidays_csv_path:
            holidays = load_holidays_csv(cfg.calendar.holidays_csv_path)
        tdays = build_trading_days(df, holidays)
        df = add_next_close_calendar(df, tdays)
    else:
        df = add_next_close(df)
    info("Göstergeler hesaplanıyor...")
    df_ind = compute_indicators(df, cfg.indicators.params)
    info("Filtre CSV okunuyor...")
    try:
        filters_df = load_filters_csv(cfg.data.filters_csv)
    except FileNotFoundError as exc:
        info(str(exc))
        filters_df = pd.DataFrame(columns=["FilterCode", "PythonQuery"])
    if filters_df.empty:
        info("Filtre CSV boş veya bulunamadı, işlem yapılmadı.")
        return
    day = pd.to_datetime(date_str).normalize()
    sigs = run_screener(df_ind, filters_df, day)
    trades = run_1g_returns(df_ind, sigs)
    xu100_pct = None
    if cfg.benchmark.xu100_source == "csv" and cfg.benchmark.xu100_csv_path:
        s = load_xu100_pct(cfg.benchmark.xu100_csv_path)
        xu100_pct = {day: float(s.get(day, float("nan")))}
    if not trades.empty:
        pivot = (
            trades.groupby(["FilterCode", "Date"])["ReturnPct"]
            .mean()
            .unstack(fill_value=float("nan"))
        )
        pivot["Ortalama"] = pivot.mean(axis=1)
        winrate = (
            trades.groupby(["FilterCode", "Date"])["Win"]
            .mean()
            .unstack(fill_value=float("nan"))
        )
        winrate["Ortalama"] = winrate.mean(axis=1)
    else:
        pivot = pd.DataFrame(columns=[day, "Ortalama"])
        winrate = pd.DataFrame()  # TİP DÜZELTİLDİ
    out_dir = resolve_path(cfg.project.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_xlsx = out_dir / f"SCAN_{day.date()}.xlsx"
    info("Raporlar yazılıyor...")
    val_sum = dataset_summary(df)
    val_iss = quality_warnings(df)
    write_reports(
        trades,
        [day],
        pivot,
        xu100_pct,
        out_xlsx=out_xlsx,
        out_csv_dir=None,
        validation_summary=val_sum,
        validation_issues=val_iss,
        summary_winrate=winrate,
        daily_sheet_prefix=cfg.report.daily_sheet_prefix,
        summary_sheet_name=cfg.report.summary_sheet_name,
        percent_fmt=cfg.report.percent_format,
    )
    info(f"Bitti. Çıktı: {out_xlsx}")


if __name__ == "__main__":
    cli()
