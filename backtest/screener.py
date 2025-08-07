# DÜZENLENDİ – SYNTAX TEMİZLİĞİ
from __future__ import annotations

import re
import warnings

import pandas as pd
from loguru import logger

from backtest.query_parser import SafeQuery


def _to_pandas_ops(expr: str) -> str:
    expr = re.sub(r"\bAND\b", "&", expr, flags=re.I)
    expr = re.sub(r"\bOR\b", "|", expr, flags=re.I)
    expr = re.sub(r"\bNOT\b", "~", expr, flags=re.I)
    return expr


def run_screener(df_ind: pd.DataFrame, filters_df: pd.DataFrame, date) -> pd.DataFrame:
    logger.debug(
        "run_screener start - data rows: {rows_df}, filter rows: {rows_filters}, date: {day}",
        rows_df=len(df_ind) if isinstance(df_ind, pd.DataFrame) else "?",
        rows_filters=len(filters_df) if isinstance(filters_df, pd.DataFrame) else "?",
        day=date,
    )

    if not isinstance(df_ind, pd.DataFrame):
        logger.error("df_ind must be a DataFrame")
        raise TypeError("df_ind must be a DataFrame")
    if not isinstance(filters_df, pd.DataFrame):
        logger.error("filters_df must be a DataFrame")
        raise TypeError("filters_df must be a DataFrame")

    if df_ind.empty:
        logger.error("df_ind is empty")
        raise ValueError("df_ind is empty")
    if filters_df.empty:
        logger.error("filters_df is empty")
        raise ValueError("filters_df is empty")

    req_df = {"symbol", "date", "open", "high", "low", "close", "volume"}
    missing_df = req_df.difference(df_ind.columns)
    if missing_df:
        msg = f"df_ind missing columns: {', '.join(sorted(missing_df))}"
        logger.error(msg)
        raise ValueError(msg)
    if not {"FilterCode", "PythonQuery"}.issubset(filters_df.columns):
        msg = "filters_df missing required columns"
        logger.error(msg)
        raise ValueError(msg)

    day = pd.to_datetime(date).date()
    d = df_ind[df_ind["date"] == day].copy()
    if d.empty:
        logger.warning("No data for date {day}", day=day)
        return pd.DataFrame(columns=["FilterCode", "Symbol", "Date"])
    d = d.reset_index(drop=True)
    out_rows = []
    for _, row in filters_df.iterrows():
        code = str(row["FilterCode"]).strip()
        expr = str(row["PythonQuery"])
        expr = _to_pandas_ops(expr)
        safe = SafeQuery(expr)
        if not safe.is_safe:
            continue
        try:
            hits = safe.filter(d)
            if not hits.empty:
                for sym in hits["symbol"]:
                    out_rows.append({"FilterCode": code, "Symbol": sym, "Date": day})
        except Exception as err:
            warnings.warn(f"Filter {code!r} failed: {err}")
            logger.warning("Filter {code!r} failed: {err}", code=code, err=err)
            continue
    if not out_rows:
        logger.debug("run_screener end - no hits")
        return pd.DataFrame(columns=["FilterCode", "Symbol", "Date"])
    out = pd.DataFrame(out_rows)
    logger.debug("run_screener end - produced {rows_out} rows", rows_out=len(out))
    return out
