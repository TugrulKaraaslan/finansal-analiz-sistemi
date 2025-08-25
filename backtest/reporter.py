from __future__ import annotations

import json
import logging
import os
import re
import warnings
from datetime import date, datetime
from pathlib import Path
from typing import Iterable, Literal, Mapping, Optional

import pandas as pd

from utils.paths import resolve_path

logger = logging.getLogger("summary_bist")


def _append_event(event: dict) -> None:
    """Append *event* as JSON line to events.jsonl if possible."""

    log_dir = os.getenv("LOG_DIR", "loglar")
    path = Path(log_dir) / "events.jsonl"
    try:  # pragma: no cover - best effort
        with path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(event, ensure_ascii=False) + "\n")
    except Exception:
        pass


def _add_bist_columns(
    summary_wide: pd.DataFrame, xu100_pct: Optional[Mapping]
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Return summary with BIST-relative metrics and a compact sheet.

    Parameters
    ----------
    summary_wide : pd.DataFrame
        Wide table with daily returns. May contain ``Ortalama`` and
        ``TradeCount`` columns which will be replaced by new metric names.
    xu100_pct : Mapping or None
        Mapping of date -> BIST100 daily return percentage.

    Returns
    -------
    (summary_wide, ratio_summary)
        ``summary_wide`` augmented with metric columns and ``ratio_summary``
        containing only metric columns sorted by ``ALPHA_RET``.
    """

    if summary_wide is None or summary_wide.empty:
        return (
            summary_wide if summary_wide is not None else pd.DataFrame(),
            pd.DataFrame(),
        )

    day_cols = [c for c in summary_wide.columns if c not in {"Ortalama", "TradeCount"}]
    sw = summary_wide[day_cols].copy()
    result = summary_wide.copy()

    result["MEAN_RET"] = sw.mean(axis=1)
    result["HIT_RATIO"] = (sw > 0).sum(axis=1) / sw.count(axis=1)
    if "TradeCount" in result.columns:
        result["N_TRADES"] = result["TradeCount"]
    else:
        result["N_TRADES"] = pd.NA

    if xu100_pct is not None:
        bist_series = pd.Series(dict(xu100_pct), dtype=float).reindex(day_cols)
        mask = sw.notna() & bist_series.notna()
        result["BIST_MEAN_RET"] = (mask.astype(float) * bist_series).sum(axis=1) / mask.sum(axis=1)
    else:
        result["BIST_MEAN_RET"] = float("nan")

    result["ALPHA_RET"] = result["MEAN_RET"] - result["BIST_MEAN_RET"]

    # logging per filter/side
    for idx, row in result.iterrows():
        n_days = sw.loc[idx].count()
        miss = len(day_cols) - n_days
        logger.info(
            "filter=%s days=%d missing=%d mean=%.6f bist_mean=%.6f",
            idx,
            n_days,
            miss,
            row["MEAN_RET"],
            row["BIST_MEAN_RET"],
        )

    result = result.drop(columns=[c for c in ["Ortalama", "TradeCount"] if c in result.columns])

    metric_cols = [
        "MEAN_RET",
        "BIST_MEAN_RET",
        "ALPHA_RET",
        "HIT_RATIO",
        "N_TRADES",
    ]
    ordered = [c for c in day_cols if c not in metric_cols] + metric_cols
    result = result[ordered]

    ratio_summary = result[metric_cols].sort_values("ALPHA_RET", ascending=False)
    return result, ratio_summary


def _ensure_dir(path: Optional[str | Path]):
    if not path:
        return
    p = resolve_path(path)
    target = p if not p.suffix else p.parent
    target.mkdir(parents=True, exist_ok=True)


def _sanitize_filename(name: str) -> str:
    """Remove characters that are invalid in file names."""
    return re.sub(r'[<>:"/\\|?*]', "_", name)


def _handle_overwrite(path: Path, policy: Literal["replace", "fail", "timestamp"]):
    """Return a safe path according to overwrite policy."""
    if policy not in {"replace", "fail", "timestamp"}:
        raise ValueError("invalid overwrite policy")
    if policy == "replace":
        return path
    if policy == "fail":
        if path.exists():
            raise FileExistsError(path)
        return path
    if path.exists():
        stamp = datetime.now().strftime("%H%M%S")
        return path.with_name(f"{path.stem}_{stamp}{path.suffix}")
    return path


def write_reports(
    trades_all: pd.DataFrame,
    dates: Optional[Iterable] = None,
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
    with_bist_ratio_summary: bool = False,
    *,
    per_day_output: bool = False,
    csv_also: bool = True,
    overwrite: Literal["replace", "fail", "timestamp"] = "replace",
    filename_pattern: str = "{date}.xlsx",
    csv_filename_pattern: str = "{date}.csv",
    separate_dir_for_range: bool = False,
):
    """Write daily/summary and optional sheets and return output paths.
    - SUMMARY: ReturnPct ortalamaları (sayısal 0.00 -> yüzde puan)
    - SUMMARY_WINRATE: Win-rate (0..1) (% format)
    - SUMMARY_DIFF: Filtre − BIST
    - VALIDATION_SUMMARY / VALIDATION_ISSUES: veri kalite raporu

    Returns
    -------
    dict
        Mapping of produced files. Keys are ``excel`` for the workbook or list
        of workbooks and ``csv`` for a list of CSV exports (if requested).
    """
    if not isinstance(trades_all, pd.DataFrame):
        raise TypeError("trades_all must be a DataFrame")
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
        raise ValueError(f"trades_all missing columns: {', '.join(sorted(missing))}")
    if "Reason" not in trades_all.columns:
        trades_all["Reason"] = pd.NA
    n_cols = trades_all.shape[1]
    if summary_wide is not None and not isinstance(summary_wide, pd.DataFrame):
        raise TypeError("summary_wide must be a DataFrame or None")
    if summary_winrate is not None and not isinstance(summary_winrate, pd.DataFrame):
        raise TypeError("summary_winrate must be a DataFrame or None")
    if validation_summary is not None and not isinstance(validation_summary, pd.DataFrame):
        raise TypeError("validation_summary must be a DataFrame or None")
    if validation_issues is not None and not isinstance(validation_issues, pd.DataFrame):
        raise TypeError("validation_issues must be a DataFrame or None")

    if dates is None:
        dates = tuple()
    elif isinstance(dates, (str, bytes, pd.Timestamp, date)):
        dates = (dates,)
    elif isinstance(dates, Iterable):
        dates = tuple(dates)
    else:
        raise TypeError("dates must be iterable or date-like")
    outputs: dict[str, Path | list[Path]] = {}
    if per_day_output:
        if not out_xlsx:
            raise ValueError("out_xlsx directory required for per_day_output")
        base_dir = resolve_path(out_xlsx)
        base_dir.mkdir(parents=True, exist_ok=True)
        if separate_dir_for_range and dates:
            start = pd.to_datetime(dates[0]).date()
            end = pd.to_datetime(dates[-1]).date()
            base_dir = base_dir / f"{start}_{end}"
            base_dir.mkdir(parents=True, exist_ok=True)
        excel_paths: list[Path] = []
        csv_paths: list[Path] = []
        for d in dates:
            day_ts = pd.to_datetime(d).normalize()
            day_df = trades_all[trades_all["Date"] == day_ts].copy()
            day_df = day_df.sort_values(["FilterCode", "Symbol"])
            day_str = str(day_ts.date())
            fname = _sanitize_filename(filename_pattern.format(date=day_str))
            xlsx_path = _handle_overwrite(base_dir / fname, overwrite)
            writer = pd.ExcelWriter(xlsx_path, engine="xlsxwriter")
            with writer:
                day_df.to_excel(writer, sheet_name="SCAN", index=False)
                summary_df = pd.DataFrame(
                    {
                        "N_TRADES": [len(day_df)],
                        "MEAN_RET": [day_df["ReturnPct"].mean()],
                        "HIT_RATIO": [day_df["Win"].mean()],
                    }
                )
                summary_df.to_excel(writer, sheet_name="SUMMARY", index=False)
            excel_paths.append(xlsx_path)
            csv_written = None
            if csv_also:
                csv_name = _sanitize_filename(csv_filename_pattern.format(date=day_str))
                csv_written = _handle_overwrite(base_dir / csv_name, overwrite)
                day_df.to_csv(csv_written, index=False, encoding="utf-8")
                csv_paths.append(csv_written)
            rows_written = len(day_df)
            event = {
                "event": "WRITE_DAY",
                "day": day_str,
                "rows_written": rows_written,
                "xlsx_path": str(xlsx_path),
            }
            if csv_written is not None:
                event["csv_path"] = str(csv_written)
            _append_event(event)
            logger.info(
                "WRITE_DAY day=%s rows_written=%d xlsx_path=%s csv_path=%s",
                day_str,
                rows_written,
                xlsx_path,
                csv_written,
            )
            if rows_written == 0:
                logger.info("WRITE_DAY_ZERO day=%s", day_str)
        outputs["excel"] = excel_paths
        if csv_paths:
            outputs["csv"] = csv_paths
        rows_total = len(trades_all)
        event = {
            "event": "WRITE_RANGE",
            "rows_total": rows_total,
            "out_dir": str(base_dir),
        }
        _append_event(event)
        logger.info(
            "WRITE_RANGE rows_total=%d out_dir=%s",
            rows_total,
            base_dir,
        )
        if rows_total == 0:
            logger.info("ZERO_RESULT_RANGE out_dir=%s", base_dir)
        return outputs
    if summary_wide is None:
        summary_wide = pd.DataFrame()
        bist_ratio_summary = pd.DataFrame()
    else:
        summary_wide, bist_ratio_summary = _add_bist_columns(summary_wide, xu100_pct)

    metric_cols = ["MEAN_RET", "BIST_MEAN_RET", "ALPHA_RET", "HIT_RATIO", "N_TRADES"]
    if out_xlsx:
        out_xlsx_path = resolve_path(out_xlsx)
        _ensure_dir(out_xlsx_path)
        try:
            writer = pd.ExcelWriter(out_xlsx_path, engine="xlsxwriter")
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

                if with_bist_ratio_summary and not bist_ratio_summary.empty:
                    bist_ratio_summary.to_excel(writer, sheet_name="BIST_RATIO_SUMMARY")

                if summary_winrate is not None and not summary_winrate.empty:
                    summary_winrate.to_excel(writer, sheet_name=f"{summary_sheet_name}_WINRATE")

                day_cols = [c for c in summary_wide.columns if c not in metric_cols]
                if xu100_pct is not None:
                    if isinstance(xu100_pct, pd.Series):
                        xu100_series = xu100_pct.astype(float)
                    elif isinstance(xu100_pct, Mapping):
                        xu100_series = pd.Series(dict(xu100_pct), dtype=float)
                    else:
                        raise TypeError("xu100_pct must be a mapping or Series")
                    if set(day_cols).issubset(set(xu100_series.index)):
                        diff = summary_wide[day_cols].copy()
                        for c in day_cols:
                            diff[c] = diff[c] - float(xu100_series.get(c, float("nan")))
                        diff["MEAN_RET"] = diff.mean(axis=1)
                        diff.to_excel(writer, sheet_name=f"{summary_sheet_name}_DIFF")
                    avg = float(xu100_series.mean()) if not xu100_series.empty else float("nan")
                    bist = (
                        pd.DataFrame(
                            [[xu100_series.get(c, float("nan")) for c in day_cols] + [avg]],
                            index=["BIST"],
                            columns=day_cols + ["MEAN_RET"],
                        )
                        if day_cols
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
                    validation_issues.to_excel(writer, sheet_name="VALIDATION_ISSUES", index=False)

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
                    last_row = rows if rows > 0 else 0
                    ws.autofilter(0, 0, last_row, n_cols - 1)

                if summary_sheet_name in writer.sheets:
                    ws = writer.sheets[summary_sheet_name]
                    idx_cols = summary_wide.index.nlevels
                    ws.set_column(idx_cols, 100, 12, num_fmt)

                wr_sheet = f"{summary_sheet_name}_WINRATE"
                if wr_sheet in writer.sheets:
                    ws = writer.sheets[wr_sheet]
                    idx_cols = summary_winrate.index.nlevels if summary_winrate is not None else 1
                    ws.set_column(idx_cols, 100, 12, pct_fmt)

                diff_sheet = f"{summary_sheet_name}_DIFF"
                if diff_sheet in writer.sheets:
                    ws = writer.sheets[diff_sheet]
                    idx_cols = summary_wide.index.nlevels
                    ws.set_column(idx_cols, 100, 12, num_fmt)
            if out_xlsx_path.exists():
                outputs["excel"] = out_xlsx_path
            else:
                warnings.warn(f"Excel yazılamadı: {out_xlsx_path}")

    if out_csv_dir and csv_also:
        out_csv_path = resolve_path(out_csv_dir)
        out_csv_path.mkdir(parents=True, exist_ok=True)
        csv_paths: list[Path] = []
        try:
            daily_csv = out_csv_path / "daily_trades.csv"
            trades_all.to_csv(
                daily_csv,
                index=False,
                encoding="utf-8",
            )
            csv_paths.append(daily_csv)
            summary_csv = out_csv_path / "summary.csv"
            summary_wide.to_csv(summary_csv, encoding="utf-8")
            csv_paths.append(summary_csv)
            if summary_winrate is not None and not summary_winrate.empty:
                winrate_csv = out_csv_path / "summary_winrate.csv"
                summary_winrate.to_csv(
                    winrate_csv,
                    encoding="utf-8",
                )
                csv_paths.append(winrate_csv)
            if validation_summary is not None and not validation_summary.empty:
                val_sum_csv = out_csv_path / "validation_summary.csv"
                validation_summary.to_csv(
                    val_sum_csv,
                    index=False,
                    encoding="utf-8",
                )
                csv_paths.append(val_sum_csv)
            if validation_issues is not None and not validation_issues.empty:
                val_iss_csv = out_csv_path / "validation_issues.csv"
                validation_issues.to_csv(
                    val_iss_csv,
                    index=False,
                    encoding="utf-8",
                )
                csv_paths.append(val_iss_csv)
        except Exception:
            warnings.warn(f"CSV yazılamadı: {out_csv_path}")
        else:
            missing = [p for p in csv_paths if not p.exists()]
            if missing:
                warnings.warn(f"CSV yazılamadı: {missing}")
            outputs["csv"] = [p for p in csv_paths if p.exists()]
    rows_total = len(trades_all)
    if out_csv_dir:
        out_dir = resolve_path(out_csv_dir)
    elif out_xlsx:
        out_dir = resolve_path(out_xlsx).parent
    else:
        out_dir = Path(".")
    event = {
        "event": "WRITE_RANGE",
        "rows_total": rows_total,
        "out_dir": str(out_dir),
    }
    _append_event(event)
    logger.info(
        "WRITE_RANGE rows_total=%d out_dir=%s",
        rows_total,
        out_dir,
    )
    if rows_total == 0:
        logger.info("ZERO_RESULT_RANGE out_dir=%s", out_dir)
    return outputs
