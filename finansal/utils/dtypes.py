"""Dtype helpers for safe column assignment."""

from __future__ import annotations

import pandas as pd

import config


def safe_set(df: pd.DataFrame, column: str, values) -> None:
    """Assign series to DataFrame with dtype safety."""
    series = pd.Series(values)

    target_dtype = config.DTYPES_MAP.get(column)
    if target_dtype is None and column in df.columns:
        target_dtype = df[column].dtype

    if target_dtype is not None:
        try:
            series = series.astype(target_dtype)
        except (ValueError, TypeError):
            # fall back to float if incompatible (e.g., float into int column)
            series = series.astype("float32")

    df[column] = series
