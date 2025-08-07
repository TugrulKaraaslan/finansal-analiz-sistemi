# DÜZENLENDİ – SYNTAX TEMİZLİĞİ
from __future__ import annotations

import re
import warnings

import pandas as pd

from backtest.query_parser import SafeQuery


def _to_pandas_ops(expr: str) -> str:
    expr = re.sub(r"\bAND\b", "&", expr, flags=re.I)
    expr = re.sub(r"\bOR\b", "|", expr, flags=re.I)
    expr = re.sub(r"\bNOT\b", "~", expr, flags=re.I)
    return expr


def run_screener(df_ind: pd.DataFrame, filters_df: pd.DataFrame, date) -> pd.DataFrame:
    if not isinstance(df_ind, pd.DataFrame):
        raise TypeError("df_ind must be a DataFrame")  # TİP DÜZELTİLDİ
    if not isinstance(filters_df, pd.DataFrame):
        raise TypeError("filters_df must be a DataFrame")  # TİP DÜZELTİLDİ
    req_df = {"symbol", "date", "open", "high", "low", "close", "volume"}
    missing_df = req_df.difference(df_ind.columns)
    if missing_df:
        raise ValueError(
            f"df_ind missing columns: {', '.join(sorted(missing_df))}"
        )  # TİP DÜZELTİLDİ
    if not {"FilterCode", "PythonQuery"}.issubset(filters_df.columns):
        raise ValueError("filters_df missing required columns")  # TİP DÜZELTİLDİ
    day = pd.to_datetime(date).date()
    d = df_ind[df_ind["date"] == day].copy()
    if d.empty:
        return pd.DataFrame(columns=["FilterCode", "Symbol", "Date", "mask"])
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
                    out_rows.append(
                        {"FilterCode": code, "Symbol": sym, "Date": day, "mask": True}
                    )
        except Exception as err:
            warnings.warn(f"Filter {code!r} failed: {err}")
            continue
    if not out_rows:
        return pd.DataFrame(
            columns=["FilterCode", "Symbol", "Date", "mask"]
        )  # TİP DÜZELTİLDİ
    return pd.DataFrame(out_rows)  # TİP DÜZELTİLDİ
