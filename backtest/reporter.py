# DÜZENLENDİ – SYNTAX TEMİZLİĞİ
from __future__ import annotations

import warnings
from datetime import date  # TİP DÜZELTİLDİ
from pathlib import Path
from typing import Iterable, Mapping, Optional  # TİP DÜZELTİLDİ

import pandas as pd

from utils.paths import resolve_path


def _ensure_dir(path: Optional[str | Path]):
    if not path:
        return
    p = resolve_path(path)
    target = p if not p.suffix else p.parent
    target.mkdir(parents=True, exist_ok=True)


def write_reports(
    trades_all: pd.DataFrame,
    dates: Optional[Iterable] = None,  # TİP DÜZELTİLDİ
    summary_wide: Optional[pd.DataFrame] = None,
    xu100_pct: Optional[Mapping] = None,
    out_xlsx: Optional[str] = None,
    out_csv_dir: Optional[str] = None,
    daily_sheet_prefix: str = "SCAN_",
    summary_sheet_name: str = "SUMMARY",
    percent_fmt: str = "0.00%",
    summary_winrate: Optional[pd.DataFrame] = None,
    validation_summary: Optional[pd.DataFrame] = None,
    validation_issues: Optional[pd.DataFrame] = None,
):
    """Write daily/summary and optional sheets and return output paths.
    - SUMMARY: ReturnPct ortalamaları (sayısal 0.00 -> yüzde puan)
    - SUMMARY_WINRATE: Win-rate (0..1) (% format)
    - SUMMARY_DIFF: Filtre − BIST
    - VALIDATION_SUMMARY / VALIDATION_ISSUES: veri kalite raporu

    Returns
    -------
    dict
        Mapping of produced files. Keys are ``excel`` for the workbook and
        ``csv`` for a list of CSV exports (if requested).
    """
    if not isinstance(trades_all, pd.DataFrame):
        raise TypeError("trades_all must be a DataFrame")  # TİP DÜZELTİLDİ
    req_cols = {
        "FilterCode",
        "Symbol",
        "Date",
        "EntryClose",
        "ExitClose",
        "ReturnPct",
        "Win",
    }
    missing = req_cols.difference(trades_all.columns)
    if missing:
        raise ValueError(
            f"trades_all missing columns: {', '.join(sorted(missing))}"
        )  # TİP DÜZELTİLDİ
    if "Reason" not in trades_all.columns:
        trades_all["Reason"] = pd.NA
    if summary_wide is not None and not isinstance(summary_wide, pd.DataFrame):
        raise TypeError("summary_wide must be a DataFrame or None")  # TİP DÜZELTİLDİ
    if summary_winrate is not None and not isinstance(summary_winrate, pd.DataFrame):
        raise TypeError("summary_winrate must be a DataFrame or None")  # TİP DÜZELTİLDİ
    if validation_summary is not None and not isinstance(
        validation_summary, pd.DataFrame
    ):
        raise TypeError(
            "validation_summary must be a DataFrame or None"
        )  # TİP DÜZELTİLDİ
    if validation_issues is not None and not isinstance(
        validation_issues, pd.DataFrame
    ):
        raise TypeError(
            "validation_issues must be a DataFrame or None"
        )  # TİP DÜZELTİLDİ

    if dates is None:
        dates = tuple()  # TİP DÜZELTİLDİ
    elif isinstance(dates, (str, bytes, pd.Timestamp, date)):
        dates = (dates,)  # TİP DÜZELTİLDİ
    elif isinstance(dates, Iterable):
        dates = tuple(dates)  # TİP DÜZELTİLDİ
    else:
        raise TypeError("dates must be iterable or date-like")  # TİP DÜZELTİLDİ
    outputs: dict[str, Path | list[Path]] = {}
    if summary_wide is None:
        summary_wide = pd.DataFrame()  # TİP DÜZELTİLDİ
    if out_xlsx:
        out_xlsx_path = resolve_path(out_xlsx)
        _ensure_dir(out_xlsx_path)
        try:
            writer = pd.ExcelWriter(
                out_xlsx_path, engine="xlsxwriter"
            )  # PATH DÜZENLENDİ
        except Exception as exc:
            raise RuntimeError(f"Excel yazılamadı: {out_xlsx_path}") from exc
        else:
            with writer:
                for d in dates:
                    day_ts = pd.to_datetime(d).normalize()
                    day_df = trades_all[trades_all["Date"] == day_ts].copy()
                    day_df = day_df.sort_values(["FilterCode", "Symbol"])
                    sheet = f"{daily_sheet_prefix}{day_ts.date()}"
                    day_df.to_excel(writer, sheet_name=sheet, index=False)

                summary_wide.to_excel(writer, sheet_name=summary_sheet_name)

                if summary_winrate is not None and not summary_winrate.empty:
                    summary_winrate.to_excel(
                        writer, sheet_name=f"{summary_sheet_name}_WINRATE"
                    )

                if xu100_pct is not None:
                    if isinstance(xu100_pct, pd.Series):
                        xu100_series = xu100_pct.astype(float)  # TİP DÜZELTİLDİ
                    elif isinstance(xu100_pct, Mapping):
                        xu100_series = pd.Series(
                            dict(xu100_pct), dtype=float
                        )  # TİP DÜZELTİLDİ
                    else:
                        raise TypeError(
                            "xu100_pct must be a mapping or Series"
                        )  # TİP DÜZELTİLDİ
                    cols = [c for c in summary_wide.columns if c != "Ortalama"]
                    if set(cols).issubset(set(xu100_series.index)):
                        diff = summary_wide.copy()
                        for c in cols:
                            diff[c] = diff[c] - float(xu100_series.get(c, float("nan")))
                        diff["Ortalama"] = diff[cols].mean(axis=1)
                        diff.to_excel(writer, sheet_name=f"{summary_sheet_name}_DIFF")
                    avg = (
                        float(xu100_series.mean())
                        if not xu100_series.empty
                        else float("nan")
                    )
                    bist = (
                        pd.DataFrame(
                            [[xu100_series.get(c, float("nan")) for c in cols] + [avg]],
                            index=["BIST"],
                            columns=cols + ["Ortalama"],
                        )
                        if cols
                        else pd.DataFrame()
                    )
                    if not bist.empty:
                        bist.to_excel(writer, sheet_name="BIST")

                # Optional validation
                if validation_summary is not None and not validation_summary.empty:
                    validation_summary.to_excel(
                        writer, sheet_name="VALIDATION_SUMMARY", index=False
                    )
                if validation_issues is not None and not validation_issues.empty:
                    validation_issues.to_excel(
                        writer, sheet_name="VALIDATION_ISSUES", index=False
                    )

                wb = writer.book
                num_fmt = wb.add_format({"num_format": "0.00"})
                pct_fmt = wb.add_format({"num_format": percent_fmt})

                for d in dates:
                    day_ts = pd.to_datetime(d).normalize()
                    sheet = f"{daily_sheet_prefix}{day_ts.date()}"
                    ws = writer.sheets[sheet]
                    ws.set_column(0, 2, 12)
                    ws.set_column(3, 4, 12)
                    ws.set_column(5, 5, 10, num_fmt)
                    ws.set_column(6, 6, 8)
                    rows = len(trades_all[trades_all["Date"] == day_ts])
                    last_row = rows if rows > 0 else 0  # LOJİK HATASI DÜZELTİLDİ
                    ws.autofilter(0, 0, last_row, day_df.shape[1] - 1)

                if summary_sheet_name in writer.sheets:
                    ws = writer.sheets[summary_sheet_name]
                    ws.set_column(1, 100, 12, num_fmt)

                wr_sheet = f"{summary_sheet_name}_WINRATE"
                if wr_sheet in writer.sheets:
                    ws = writer.sheets[wr_sheet]
                    ws.set_column(1, 100, 12, pct_fmt)

                diff_sheet = f"{summary_sheet_name}_DIFF"
                if diff_sheet in writer.sheets:
                    ws = writer.sheets[diff_sheet]
                    ws.set_column(1, 100, 12, num_fmt)
            if out_xlsx_path.exists():
                outputs["excel"] = out_xlsx_path
            else:
                warnings.warn(f"Excel yazılamadı: {out_xlsx_path}")

    if out_csv_dir:
        out_csv_path = resolve_path(out_csv_dir)
        out_csv_path.mkdir(parents=True, exist_ok=True)
        csv_paths: list[Path] = []
        try:
            daily_csv = out_csv_path / "daily_trades.csv"
            trades_all.to_csv(
                daily_csv,
                index=False,
                encoding="utf-8",
            )  # PATH DÜZENLENDİ
            csv_paths.append(daily_csv)
            summary_csv = out_csv_path / "summary.csv"
            summary_wide.to_csv(summary_csv, encoding="utf-8")  # PATH DÜZENLENDİ
            csv_paths.append(summary_csv)
            if summary_winrate is not None and not summary_winrate.empty:
                winrate_csv = out_csv_path / "summary_winrate.csv"
                summary_winrate.to_csv(
                    winrate_csv,
                    encoding="utf-8",
                )  # PATH DÜZENLENDİ
                csv_paths.append(winrate_csv)
            if validation_summary is not None and not validation_summary.empty:
                val_sum_csv = out_csv_path / "validation_summary.csv"
                validation_summary.to_csv(
                    val_sum_csv,
                    index=False,
                    encoding="utf-8",
                )  # PATH DÜZENLENDİ
                csv_paths.append(val_sum_csv)
            if validation_issues is not None and not validation_issues.empty:
                val_iss_csv = out_csv_path / "validation_issues.csv"
                validation_issues.to_csv(
                    val_iss_csv,
                    index=False,
                    encoding="utf-8",
                )  # PATH DÜZENLENDİ
                csv_paths.append(val_iss_csv)
        except Exception:
            warnings.warn(f"CSV yazılamadı: {out_csv_path}")  # PATH DÜZENLENDİ
        else:
            missing = [p for p in csv_paths if not p.exists()]
            if missing:
                warnings.warn(f"CSV yazılamadı: {missing}")
            outputs["csv"] = [p for p in csv_paths if p.exists()]
    return outputs
