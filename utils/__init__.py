"""Common helper utilities for the analysis project.

This package bundles crossover detection, filter-column extraction and log
maintenance helpers used by the CLI and reporting modules.
"""

from __future__ import annotations

from functools import lru_cache
from io import StringIO

import pandas as pd

from finansal_analiz_sistemi.logging_config import get_logger

from .purge_old_logs import purge_old_logs

__all__ = [
    "crosses_above",
    "crosses_below",
    "extract_columns_from_filters",
    "extract_columns_from_filters_cached",
    "purge_old_logs",
]

logger = get_logger(__name__)


def _align(a: pd.Series, b: pd.Series) -> tuple[pd.Series, pd.Series]:
    """Return ``a`` and ``b`` aligned to their common index.

    Parameters
    ----------
    a, b : pd.Series
        Series to be aligned.

    Returns
    -------
    tuple[pd.Series, pd.Series]
        ``(a, b)`` reindexed to the intersection of their indices.

    """
    x, y = a.align(b, join="inner")
    return x, y


def _crosses(a: pd.Series, b: pd.Series, above: bool) -> pd.Series:
    """Return ``True`` where ``a`` crosses ``b`` in the given direction.

    Parameters
    ----------
    a, b : pd.Series
        Series to compare.
    above : bool
        ``True`` to detect upward crossovers, ``False`` for downward.

    Returns
    -------
    pd.Series
        Boolean mask indexed like the aligned input series.

    """
    if a is None or b is None:
        return pd.Series(False, index=[])
    x, y = _align(a, b)
    if above:
        return (x.shift(1) < y.shift(1)) & (x >= y)
    return (x.shift(1) > y.shift(1)) & (x <= y)


def crosses_above(a: pd.Series, b: pd.Series) -> pd.Series:
    """Return ``True`` where ``a`` crosses above ``b``."""
    return _crosses(a, b, True)


def crosses_below(a: pd.Series, b: pd.Series) -> pd.Series:
    """Return ``True`` where ``a`` crosses below ``b``."""
    return _crosses(a, b, False)


def extract_columns_from_filters(
    df_filters: pd.DataFrame | None,
    series_series: list | None,
    series_value: list | None,
) -> set:
    """Return column names referenced in filters and crossovers.

    Parameters
    ----------
    df_filters : pd.DataFrame | None
        Loaded filter definitions.
    series_series : list | None
        List of series-to-series crossover tuples.
    series_value : list | None
        List of series-to-value crossover tuples.

    Returns
    -------
    set
        Unique column names required for indicator computation.

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
) -> set:
    """Return referenced columns using a CSV string for caching.

    Parameters
    ----------
    df_filters_csv : str
        Filter definitions serialized as CSV.
    series_series : list | None
        Series-to-series crossover configuration.
    series_value : list | None
        Series-to-value crossover configuration.

    Returns
    -------
    set
        Unique column names collected from the CSV content.

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
