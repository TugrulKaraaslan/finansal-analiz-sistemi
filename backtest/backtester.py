# DÜZENLENDİ – SYNTAX TEMİZLİĞİ
from __future__ import annotations

import pandas as pd


def run_1g_returns(df_with_next: pd.DataFrame, signals: pd.DataFrame) -> pd.DataFrame:
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
