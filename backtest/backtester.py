# DÜZENLENDİ – SYNTAX TEMİZLİĞİ
from __future__ import annotations

import pandas as pd
from loguru import logger


def run_1g_returns(df_with_next: pd.DataFrame, signals: pd.DataFrame) -> pd.DataFrame:
    """Calculate 1G returns for screener signals.

    Parameters
    ----------
    df_with_next:
        DataFrame containing price data with next day's close.
    signals:
        Screener output with FilterCode, Symbol and Date columns.
    """

    logger.debug(
        "run_1g_returns start - base rows: {rows_base}, signals rows: {rows_sig}",
        rows_base=len(df_with_next) if isinstance(df_with_next, pd.DataFrame) else "?",
        rows_sig=len(signals) if isinstance(signals, pd.DataFrame) else "?",
    )

    if not isinstance(df_with_next, pd.DataFrame):
        logger.error("df_with_next must be a DataFrame")
        raise TypeError("df_with_next must be a DataFrame")
    if not isinstance(signals, pd.DataFrame):
        logger.error("signals must be a DataFrame")
        raise TypeError("signals must be a DataFrame")

    if df_with_next.empty:
        logger.error("df_with_next is empty")
        raise ValueError("df_with_next is empty")
    if signals.empty:
        logger.warning("signals DataFrame is empty")
        return pd.DataFrame(
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

    req_base = {"symbol", "date", "close", "next_date", "next_close"}
    missing_base = req_base.difference(df_with_next.columns)
    if missing_base:
        msg = f"Eksik kolon(lar): {', '.join(sorted(missing_base))}"
        logger.error(msg)
        raise ValueError(msg)

    req_sig = {"FilterCode", "Symbol", "Date"}
    missing_sig = req_sig.difference(signals.columns)
    if missing_sig:
        msg = f"Eksik kolon(lar): {', '.join(sorted(missing_sig))}"
        logger.error(msg)
        raise ValueError(msg)

    base = df_with_next[["symbol", "date", "close", "next_date", "next_close"]].copy()
    merged = signals.merge(
        base, left_on=["Symbol", "Date"], right_on=["symbol", "date"], how="left"
    )
    merged = merged.drop(columns=["symbol", "date"])
    merged = merged.dropna(subset=["close", "next_close"])
    merged["EntryClose"] = merged["close"]
    merged["ExitClose"] = merged["next_close"]
    invalid = (merged["EntryClose"] <= 0) | merged["EntryClose"].isna()
    if invalid.any():
        logger.warning(
            "run_1g_returns dropping {n} rows with non-positive EntryClose",
            n=int(invalid.sum()),
        )
        merged = merged[~invalid]
    merged["ReturnPct"] = (merged["ExitClose"] / merged["EntryClose"] - 1.0) * 100.0
    merged["Win"] = merged["ReturnPct"] > 0.0

    out = merged[
        ["FilterCode", "Symbol", "Date", "EntryClose", "ExitClose", "ReturnPct", "Win"]
    ].copy()
    logger.debug("run_1g_returns end - produced {rows_out} rows", rows_out=len(out))
    return out
