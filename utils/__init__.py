"""
Common helper routines for filters and logging.

The package exposes crossover utilities, filter-column extraction
helpers and log maintenance tools shared across the project.
"""

from __future__ import annotations

from collections.abc import Iterable, Sequence
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
    """Return ``series_a`` and ``series_b`` aligned to their shared index.

    Parameters
    ----------
    series_a, series_b : pandas.Series
        Input series which may have differing indexes.

    Returns
    -------
    tuple[pandas.Series, pandas.Series]
        ``series_a`` and ``series_b`` restricted to the intersection of their
        indexes so element-wise comparisons operate safely. When both series
        already share the same index they are returned unchanged. The helper
        avoids :meth:`Series.align` for better performance on large datasets.
    """

    if series_a.index.equals(series_b.index):
        return series_a, series_b

    # ``sort=False`` preserves the order of ``series_a`` to keep comparisons
    # stable when indexes are not monotonically increasing.
    common_idx = series_a.index.intersection(series_b.index, sort=False)
    aligned_a = series_a.reindex(common_idx)
    aligned_b = series_b.reindex(common_idx)
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
        res = (prev_x < prev_y) & (x >= y)
    else:
        res = (prev_x > prev_y) & (x <= y)
    return res.fillna(False).astype(bool)


def crosses_above(a: pd.Series | None, b: pd.Series | None) -> pd.Series:
    """Return ``True`` where ``a`` crosses above ``b``."""
    return _crosses(a, b, True)


def crosses_below(a: pd.Series | None, b: pd.Series | None) -> pd.Series:
    """Return ``True`` where ``a`` crosses below ``b``."""
    return _crosses(a, b, False)


def extract_columns_from_filters(
    df_filters: pd.DataFrame | None,
    series_series: Iterable[Sequence[str]] | None,
    series_value: Iterable[Sequence[str]] | None,
) -> set[str]:
    """Return column names referenced in filters and crossovers.

    Args:
        df_filters (pd.DataFrame | None): Loaded filter definitions.
        series_series (Iterable[Sequence[str]] | None):
            Series-to-series crossover configuration.
        series_value (Iterable[Sequence[str]] | None):
            Series-to-value crossover configuration.

    Returns:
        set[str]: Unique column names required for indicator computation.
    """
    try:
        from filter_engine import _extract_query_columns
    except Exception:
        # Return an empty set when ``filter_engine`` is unavailable
        return set()

    wanted: set[str] = set()
    if (
        df_filters is not None
        and not df_filters.empty
        and "PythonQuery" in df_filters.columns
    ):
        for q in df_filters["PythonQuery"].dropna().astype(str):
            wanted.update(_extract_query_columns(q))

    wanted.update(
        part for entry in (series_series or []) if len(entry) >= 2 for part in entry[:2]
    )

    wanted.update(entry[0] for entry in (series_value or []) if entry)

    return wanted


def extract_columns_from_filters_cached(
    df_filters_csv: str,
    series_series: Iterable[Sequence[str]] | None,
    series_value: Iterable[Sequence[str]] | None,
) -> set[str]:
    """Return referenced columns using a CSV string for caching."""

    series_series_t = (
        tuple(tuple(entry) for entry in series_series) if series_series else None
    )
    series_value_t = (
        tuple(tuple(entry) for entry in series_value) if series_value else None
    )

    return _extract_columns_from_filters_cached(
        df_filters_csv, series_series_t, series_value_t
    )


@lru_cache(maxsize=1)
def _extract_columns_from_filters_cached(
    df_filters_csv: str,
    series_series: tuple[tuple[str, ...], ...] | None,
    series_value: tuple[tuple[str, ...], ...] | None,
) -> set[str]:
    """Return referenced columns using a CSV string for caching.

    Args:
        df_filters_csv (str): Filter definitions serialized as CSV.
        series_series (Iterable[Sequence[str]] | None):
            Series-to-series crossover configuration.
        series_value (Iterable[Sequence[str]] | None):
            Series-to-value crossover configuration.

    Returns:
        set[str]: Unique column names collected from the CSV content.
    """
    df_filters = None
    if df_filters_csv and df_filters_csv.strip():
        try:
            first = df_filters_csv.splitlines()[0]
            sep = ";" if first.count(";") >= first.count(",") else ","
            df_filters = pd.read_csv(
                StringIO(df_filters_csv),
                sep=sep,
                comment="#",
                dtype=str,
            )
        except Exception:
            df_filters = None

    return extract_columns_from_filters(df_filters, series_series, series_value)


# expose cache helpers on the public function
extract_columns_from_filters_cached.cache_clear = (
    _extract_columns_from_filters_cached.cache_clear
)
extract_columns_from_filters_cached.cache_info = (
    _extract_columns_from_filters_cached.cache_info
)
