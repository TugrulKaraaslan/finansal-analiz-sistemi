# DÜZENLENDİ – SYNTAX TEMİZLİĞİ
from __future__ import annotations

import pandas as pd


def normalize(df: pd.DataFrame) -> pd.DataFrame:
    if not isinstance(df, pd.DataFrame):
        raise TypeError("df must be a DataFrame")  # TİP DÜZELTİLDİ
    need = ["symbol", "date", "open", "high", "low", "close", "volume"]
    for n in need:
        if n not in df.columns:
            raise ValueError(f"Eksik zorunlu kolon: {n}")  # TİP DÜZELTİLDİ
    df = df.copy()
    df["symbol"] = df["symbol"].astype(str).str.upper().str.strip()
    df["date"] = pd.to_datetime(df["date"]).dt.date
    for c in ["open", "high", "low", "close", "volume"]:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    df = (
        df.dropna(subset=["close"])
        .sort_values(["symbol", "date"])
        .drop_duplicates(["symbol", "date"])
    )
    return df.reset_index(drop=True)
