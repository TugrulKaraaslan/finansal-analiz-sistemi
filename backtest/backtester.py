# DÜZENLENDİ – SYNTAX TEMİZLİĞİ
from __future__ import annotations

import pandas as pd


def run_1g_returns(df_with_next: pd.DataFrame, signals: pd.DataFrame) -> pd.DataFrame:
    if not isinstance(df_with_next, pd.DataFrame):
        raise TypeError("df_with_next must be a DataFrame")  # TİP DÜZELTİLDİ
    if not isinstance(signals, pd.DataFrame):
        raise TypeError("signals must be a DataFrame")  # TİP DÜZELTİLDİ
    req_base = {"symbol", "date", "close", "next_date", "next_close"}
    missing_base = req_base.difference(df_with_next.columns)
    if missing_base:
        raise ValueError(
            f"Eksik kolon(lar): {', '.join(sorted(missing_base))}"
        )  # TİP DÜZELTİLDİ
    if signals.empty:
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
    req_sig = {"FilterCode", "Symbol", "Date"}
    missing_sig = req_sig.difference(signals.columns)
    if missing_sig:
        raise ValueError(
            f"Eksik kolon(lar): {', '.join(sorted(missing_sig))}"
        )  # TİP DÜZELTİLDİ
    base = df_with_next[["symbol", "date", "close", "next_date", "next_close"]].copy()
    merged = signals.merge(
        base, left_on=["Symbol", "Date"], right_on=["symbol", "date"], how="left"
    )
    merged = merged.drop(columns=["symbol", "date"])
    merged = merged.dropna(subset=["close", "next_close"])
    merged["EntryClose"] = merged["close"]
    merged["ExitClose"] = merged["next_close"]
    merged["ReturnPct"] = (merged["ExitClose"] / merged["EntryClose"] - 1.0) * 100.0
    merged["Win"] = merged["ReturnPct"] > 0.0
    out = merged[
        ["FilterCode", "Symbol", "Date", "EntryClose", "ExitClose", "ReturnPct", "Win"]
    ].copy()
    return out
