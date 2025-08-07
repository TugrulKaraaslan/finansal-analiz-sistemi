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

    day = pd.to_datetime(date).normalize()
    d = df_ind[df_ind["date"] == day].copy()
    if d.empty:
        logger.warning("No data for date {day}", day=day)
        return pd.DataFrame(columns=["FilterCode", "Symbol", "Date"])
    d = d.reset_index(drop=True)
    filters_df = filters_df.copy()
    filters_df["FilterCode"] = filters_df["FilterCode"].astype(str).str.strip()
    filters_df["expr"] = filters_df["PythonQuery"].astype(str).map(_to_pandas_ops)
    groups = filters_df.get("Group")
    if groups is None:
        groups = [None] * len(filters_df)
    valids = []
    for code, expr, grp in zip(filters_df["FilterCode"], filters_df["expr"], groups):
        sq = SafeQuery(expr)
        if not sq.is_safe:
            logger.warning(
                "Filter skipped due to unsafe expression", code=code, expr=expr, reason=sq.error
            )
            continue
        missing_cols = sq.names.difference(d.columns)
        if missing_cols:
            msg = f"Filter {code!r} skipped; missing columns: {sorted(missing_cols)}"
            logger.warning(
                "Filter skipped due to missing columns", code=code, missing=sorted(missing_cols)
            )
            warnings.warn(msg)
            continue
        valids.append((code, grp, sq))
    out_frames = []
    if valids:
        masks = {}
        for code, _, sq in valids:
            try:
                masks[code] = sq._mask(d)
            except Exception as err:
                warnings.warn(f"Filter {code!r} failed: {err}")
                logger.warning("Filter {code!r} failed: {err}", code=code, err=err)
        mask_df = pd.DataFrame(masks)
        for (code, grp, _), (_, mask) in zip(valids, mask_df.items()):
            idx = mask[mask].index
            if not len(idx):
                continue
            tmp = d.loc[idx, ["symbol"]].copy()
            tmp["FilterCode"] = code
            if grp is not None:
                tmp["Group"] = grp
            tmp["Date"] = day
            out_frames.append(tmp)
    if not out_frames:
        logger.debug("run_screener end - no hits")
        return pd.DataFrame(columns=["FilterCode", "Symbol", "Date"])
    out = pd.concat(out_frames, ignore_index=True)
    out = out.rename(columns={"symbol": "Symbol"})
    cols = ["FilterCode"]
    if "Group" in out.columns:
        cols.append("Group")
    cols.extend(["Symbol", "Date"])
    out = out[cols]
    logger.debug("run_screener end - produced {rows_out} rows", rows_out=len(out))
    return out
