"""
Common helper routines for filters and logging.

The package exposes crossover utilities, filter-column extraction
helpers and log maintenance tools shared across the project.
"""

from __future__ import annotations

from functools import lru_cache
from io import StringIO

import pandas as pd

from .purge_old_logs import purge_old_logs

__all__ = [
    "crosses_above",
    "crosses_below",
    "extract_columns_from_filters",
    "extract_columns_from_filters_cached",
    "purge_old_logs",
]


def _align_common_index(
    series_a: pd.Series, series_b: pd.Series
) -> tuple[pd.Series, pd.Series]:
    """Return ``series_a`` and ``series_b`` aligned to their shared index."""

    aligned_a, aligned_b = series_a.align(series_b, join="inner")
    return aligned_a, aligned_b


def _crosses(
    series_a: pd.Series | None, series_b: pd.Series | None, above: bool
) -> pd.Series:
    """Return ``True`` where ``series_a`` crosses ``series_b``.

    Parameters
    ----------
    series_a, series_b : pandas.Series | None
        Series to compare. ``None`` yields an empty ``Series``.
    above : bool
        ``True`` to detect upward crossovers, ``False`` for downward.

    Returns
    -------
    pandas.Series
        Boolean mask indexed like the aligned input series.
    """

    if series_a is None or series_b is None:
        return pd.Series(dtype=bool)

    x, y = _align_common_index(series_a, series_b)
    prev_x = x.shift(1)
    prev_y = y.shift(1)

    if above:
        return (prev_x < prev_y) & (x >= y)
    return (prev_x > prev_y) & (x <= y)


def crosses_above(a: pd.Series | None, b: pd.Series | None) -> pd.Series:
    """Return ``True`` where ``a`` crosses above ``b``."""
    return _crosses(a, b, True)


def crosses_below(a: pd.Series | None, b: pd.Series | None) -> pd.Series:
    """Return ``True`` where ``a`` crosses below ``b``."""
    return _crosses(a, b, False)


def extract_columns_from_filters(
    df_filters: pd.DataFrame | None,
    series_series: list | None,
    series_value: list | None,
) -> set[str]:
    """Return column names referenced in filters and crossovers.

    Args:
        df_filters (pd.DataFrame | None): Loaded filter definitions.
        series_series (list | None): List of series-to-series crossover tuples.
        series_value (list | None): List of series-to-value crossover tuples.

    Returns:
        set[str]: Unique column names required for indicator computation.
    """
    try:
        from filter_engine import _extract_query_columns
    except Exception:
        # Return an empty set when ``filter_engine`` is unavailable
        return set()

    wanted = set()
    if (
        df_filters is not None
        and not df_filters.empty
        and "PythonQuery" in df_filters.columns
    ):
        for q in df_filters["PythonQuery"].dropna().astype(str):
            wanted |= _extract_query_columns(q)

    for entry in series_series or []:
        if len(entry) >= 2:
            wanted.add(entry[0])
            wanted.add(entry[1])

    for entry in series_value or []:
        if len(entry) >= 1:
            wanted.add(entry[0])

    return wanted


@lru_cache(maxsize=1)
def extract_columns_from_filters_cached(
    df_filters_csv: str,
    series_series: list | None,
    series_value: list | None,
) -> set[str]:
    """Return referenced columns using a CSV string for caching.

    Args:
        df_filters_csv (str): Filter definitions serialized as CSV.
        series_series (list | None): Series-to-series crossover configuration.
        series_value (list | None): Series-to-value crossover configuration.

    Returns:
        set[str]: Unique column names collected from the CSV content.
    """
    df_filters = None
    if df_filters_csv:
        try:
            first = df_filters_csv.splitlines()[0]
            sep = ";" if first.count(";") >= first.count(",") else ","
            df_filters = pd.read_csv(StringIO(df_filters_csv), sep=sep)
        except Exception:
            df_filters = None

    return extract_columns_from_filters(df_filters, series_series, series_value)
