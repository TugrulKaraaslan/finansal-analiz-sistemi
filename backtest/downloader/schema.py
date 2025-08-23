from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Optional

import pandas as pd

CANON_COLS = ["date", "open", "high", "low", "close", "volume", "quantity"]


def _to_number(val: pd.Series) -> pd.Series:
    """Convert string numbers with possible comma decimal or thousand separators."""
    if val.dtype == object:
        val = val.astype(str).str.replace(".", "", regex=False).str.replace(",", ".", regex=False)
    return pd.to_numeric(val, errors="coerce")


def normalize(df: pd.DataFrame, tz: Optional[str] = None, dayfirst: bool = False) -> pd.DataFrame:
    """Return *df* with canonical schema.

    - date column converted to datetime64[ns] and made tz-naive
    - numeric columns coerced to float64/int64
    - rows sorted by date and duplicates removed
    """
    if "date" not in df.columns:
        raise ValueError("date column missing")

    df = df.rename(columns={c: c.lower() for c in df.columns})

    df["date"] = pd.to_datetime(df["date"], dayfirst=dayfirst, errors="coerce")
    if tz:
        df["date"] = df["date"].dt.tz_convert(tz).dt.tz_localize(None)
    else:
        df["date"] = df["date"].dt.tz_localize(None)

    for col in ["open", "high", "low", "close"]:
        if col in df.columns:
            df[col] = _to_number(df[col]).astype("float64")
    for col in ["volume", "quantity"]:
        if col in df.columns:
            df[col] = _to_number(df[col]).fillna(0).astype("int64")

    df = df.dropna(subset=["date"]).sort_values("date")
    df = df.drop_duplicates(subset=["date"])
    df = df.reset_index(drop=True)
    return df[[c for c in CANON_COLS if c in df.columns]]
