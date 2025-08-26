"""Default filter definitions and validation helpers."""

from __future__ import annotations
from typing import Dict, List

import pandas as pd

REQUIRED_HEADER = ["FilterCode", "PythonQuery"]


# --- Default module-based filters ---

FILTERS: List[Dict[str, str]] = [
    {"FilterCode": "FI", "PythonQuery": "True"},
    {"FilterCode": "T1", "PythonQuery": "close > open"},
    {"FilterCode": "T2", "PythonQuery": "sma_5 > sma_10"},
]


def get_filters() -> List[Dict[str, str]]:
    return FILTERS


def validate_filters_df(df: pd.DataFrame) -> pd.DataFrame:
    """Validate filter DataFrame ensuring strict schema and content."""

    if list(df.columns) != REQUIRED_HEADER:
        raise ValueError(f"filters kolonları {REQUIRED_HEADER!r} olmalı")

    df = df.dropna(how="all")

    if df.empty:
        raise ValueError("En az bir filtre tanımı gerekli")

    if df["FilterCode"].isna().any() or df["FilterCode"].astype(str).str.strip().eq("").any():
        raise ValueError("FilterCode boş olamaz")
    if df["PythonQuery"].isna().any() or df["PythonQuery"].astype(str).str.strip().eq("").any():
        raise ValueError("PythonQuery boş olamaz")

    df["FilterCode"] = df["FilterCode"].astype(str).str.strip()
    df["PythonQuery"] = df["PythonQuery"].astype(str).str.strip()

    dups = df["FilterCode"][df["FilterCode"].duplicated()]
    if not dups.empty:
        dup_codes = ", ".join(sorted(dups.unique()))
        raise ValueError(f"Duplicate FilterCode detected: {dup_codes}")
    return df


__all__ = [
    "validate_filters_df",
    "FILTERS",
    "get_filters",
]
