# DÜZENLENDİ – SYNTAX TEMİZLİĞİ
from __future__ import annotations

import os
from typing import Dict, List, Optional

import pandas as pd


def _ensure_dir(path: str):
    os.makedirs(os.path.dirname(path), exist_ok=True)


def write_reports(
    trades_all: pd.DataFrame,
    dates: List,
    summary_wide: pd.DataFrame,
    xu100_pct: Dict = None,
    out_xlsx: str = None,
    out_csv_dir: str = None,
    daily_sheet_prefix: str = "SCAN_",
    summary_sheet_name: str = "SUMMARY",
    percent_fmt: str = "0.00%",
    summary_winrate: Optional[pd.DataFrame] = None,
    validation_summary: Optional[pd.DataFrame] = None,
    validation_issues: Optional[pd.DataFrame] = None,
):
    """Write daily/summary and optional sheets.
    - SUMMARY: ReturnPct ortalamaları (sayısal 0.00 -> yüzde puan)
    - SUMMARY_WINRATE: Win-rate (0..1) (% format)
    - SUMMARY_DIFF: Filtre − BIST
    - VALIDATION_SUMMARY / VALIDATION_ISSUES: veri kalite raporu
    """
    if out_xlsx:
        _ensure_dir(out_xlsx)
        with pd.ExcelWriter(out_xlsx, engine="xlsxwriter") as writer:
            for d in dates:
                day_df = trades_all[trades_all["Date"] == d].copy()
                day_df = day_df.sort_values(["FilterCode", "Symbol"])
                sheet = f"{daily_sheet_prefix}{d}"
                day_df.to_excel(writer, sheet_name=sheet, index=False)

            summary_wide.to_excel(writer, sheet_name=summary_sheet_name)

            if summary_winrate is not None and not summary_winrate.empty:
                summary_winrate.to_excel(
                    writer, sheet_name=f"{summary_sheet_name}_WINRATE"
                )

            if xu100_pct:
                cols = [c for c in summary_wide.columns if c != "Ortalama"]
                if set(cols).issubset(set(xu100_pct.keys())):
                    diff = summary_wide.copy()
                    for c in cols:
                        diff[c] = diff[c] - float(xu100_pct[c])
                    diff["Ortalama"] = diff[cols].mean(axis=1)
                    diff.to_excel(writer, sheet_name=f"{summary_sheet_name}_DIFF")
                bist = (
                    pd.DataFrame(
                        [
                            [xu100_pct.get(c, float("nan")) for c in cols]
                            + [pd.Series(list(xu100_pct.values())).mean()]
                        ],
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
                sheet = f"{daily_sheet_prefix}{d}"
                ws = writer.sheets[sheet]
                ws.set_column(0, 2, 12)
                ws.set_column(3, 4, 12)
                ws.set_column(5, 5, 10, num_fmt)
                ws.set_column(6, 6, 8)
                ws.autofilter(0, 0, len(trades_all[trades_all["Date"] == d]), 6)

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

    if out_csv_dir:
        os.makedirs(out_csv_dir, exist_ok=True)
        trades_all.to_csv(os.path.join(out_csv_dir, "daily_trades.csv"), index=False)
        summary_wide.to_csv(os.path.join(out_csv_dir, "summary.csv"))
        if summary_winrate is not None and not summary_winrate.empty:
            summary_winrate.to_csv(os.path.join(out_csv_dir, "summary_winrate.csv"))
        if validation_summary is not None and not validation_summary.empty:
            validation_summary.to_csv(
                os.path.join(out_csv_dir, "validation_summary.csv"), index=False
            )
        if validation_issues is not None and not validation_issues.empty:
            validation_issues.to_csv(
                os.path.join(out_csv_dir, "validation_issues.csv"), index=False
            )
