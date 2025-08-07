# DÜZENLENDİ – SYNTAX TEMİZLİĞİ
from __future__ import annotations

import pandas as pd
from loguru import logger


def run_1g_returns(
    df_with_next: pd.DataFrame,
    signals: pd.DataFrame,
    holding_period: int = 1,
    transaction_cost: float = 0.0,
) -> pd.DataFrame:
    """Calculate returns for screener signals."""

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
    if not isinstance(holding_period, int) or holding_period < 1:
        raise ValueError("holding_period must be positive int")
    if not isinstance(transaction_cost, (int, float)):
        raise TypeError("transaction_cost must be numeric")

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

    req_base = {"symbol", "date", "close"}
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

    base = df_with_next[["symbol", "date", "close"]].copy()
    base["date"] = pd.to_datetime(base["date"]).dt.normalize()
    before = len(base)
    base = base.drop_duplicates(["symbol", "date"])
    if len(base) != before:
        logger.warning("dropped {n} duplicate price rows", n=before - len(base))

    signals = signals.copy()
    signals["Date"] = pd.to_datetime(signals["Date"]).dt.normalize()
    before_sig = len(signals)
    signals = signals.drop_duplicates(["Symbol", "Date"])
    if len(signals) != before_sig:
        logger.warning("dropped {n} duplicate signal rows", n=before_sig - len(signals))

    merged = signals.merge(
        base, left_on=["Symbol", "Date"], right_on=["symbol", "date"], how="left"
    )
    merged.rename(columns={"close": "EntryClose"}, inplace=True)
    merged = merged.drop(columns=["symbol", "date"])
    merged["ExitDate"] = merged["Date"] + pd.to_timedelta(holding_period, unit="D")
    exit_base = base.rename(columns={"date": "ExitDate", "close": "ExitClose"})
    merged = merged.merge(
        exit_base, left_on=["Symbol", "ExitDate"], right_on=["symbol", "ExitDate"], how="left"
    )
    merged.drop(columns=["symbol", "ExitDate"], inplace=True)
    merged = merged.dropna(subset=["EntryClose", "ExitClose"])
    invalid = (merged["EntryClose"] <= 0) | merged["EntryClose"].isna()
    if invalid.any():
        logger.warning(
            "run_1g_returns dropping {n} rows with non-positive EntryClose",
            n=int(invalid.sum()),
        )
        merged = merged[~invalid]
    merged["ReturnPct"] = (
        (merged["ExitClose"] / merged["EntryClose"] - 1.0) * 100.0
        - float(transaction_cost)
    )
    merged["Win"] = merged["ReturnPct"] > 0.0

    out = merged[
        ["FilterCode", "Symbol", "Date", "EntryClose", "ExitClose", "ReturnPct", "Win"]
    ].copy()
    logger.debug("run_1g_returns end - produced {rows_out} rows", rows_out=len(out))
    return out
