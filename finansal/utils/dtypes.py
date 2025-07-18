"""Helpers for dtype-aware column assignment.

The :func:`safe_set` function assigns a sequence to a DataFrame column
and casts values to a suitable dtype whenever possible.
"""

from __future__ import annotations

from typing import Any, Iterable

import pandas as pd

from finansal_analiz_sistemi import config


def safe_set(df: pd.DataFrame, column: str, values: Iterable[Any]) -> None:
    """Assign ``values`` to ``df[column]`` with dtype safety.

    Args:
        df (pd.DataFrame): Target DataFrame to modify.
        column (str): Column name to assign.
        values (Iterable[Any]): Values to be set. ``values`` must be index-aligned
            with ``df``. When the length differs, values are reindexed to ``df``
            and missing entries become ``NaN``.

    """
    # Ensure the index matches the DataFrame to avoid misaligned assignment
    try:
        series = pd.Series(values, index=df.index)
    except ValueError:
        series = pd.Series(values)
        series = series.reindex(df.index)

    target_dtype = config.DTYPES_MAP.get(column)
    if target_dtype is None and column in df.columns:
        target_dtype = df[column].dtype

    if target_dtype is not None:
        try:
            series = series.astype(target_dtype)
        except (ValueError, TypeError):
            if str(target_dtype).startswith("int"):
                try:
                    nullable = "Int32" if "32" in str(target_dtype) else "Int64"
                    series = series.astype(nullable)
                except Exception:
                    series = series.astype("float32")
            else:
                series = series.astype("float32")

    df[column] = series
