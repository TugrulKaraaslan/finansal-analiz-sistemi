"""Helpers for dtype-aware column assignment.

The :func:`safe_set` function assigns a sequence to a DataFrame column
and casts values to a suitable dtype whenever possible.
"""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any

import pandas as pd
from pandas.api.types import is_integer_dtype

from finansal_analiz_sistemi import config


def safe_set(df: pd.DataFrame, column: str, values: Iterable[Any]) -> None:
    """Assign ``values`` to ``df[column]`` with dtype safety.

    Args:
        df (pd.DataFrame): Target DataFrame to modify.
        column (str): Column name to assign.
        values (Iterable[Any] | pd.Series): Values assigned to ``df``. When the
            provided series has a different index or length, it is reindexed to
            ``df`` and missing entries become ``NaN``.

    """
    # Ensure the index matches the DataFrame to avoid misaligned assignment
    if isinstance(values, pd.Series):
        series = values if values.index.equals(df.index) else values.reindex(df.index)
    else:
        items = list(values)
        try:
            series = pd.Series(items, index=df.index)
        except ValueError:
            series = pd.Series(items).reindex(df.index)

    target_dtype = config.DTYPES_MAP.get(column)
    if target_dtype is None and column in df.columns:
        target_dtype = df[column].dtype

    if target_dtype is not None:
        try:
            series = series.astype(target_dtype)
        except (ValueError, TypeError):
            if is_integer_dtype(target_dtype):
                try:
                    nullable = "Int32" if "32" in str(target_dtype) else "Int64"
                    series = series.astype(nullable)
                except Exception:
                    series = series.astype("float32")
            else:
                series = series.astype("float32")

    df[column] = series
