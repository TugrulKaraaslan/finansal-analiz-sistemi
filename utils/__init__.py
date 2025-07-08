"""Utility helpers used across the financial analysis project."""

from __future__ import annotations

from functools import lru_cache
from io import StringIO
from pathlib import Path

import pandas as pd

from finansal_analiz_sistemi.logging_config import get_logger


__all__ = [
    "crosses_above",
    "crosses_below",
    "extract_columns_from_filters",
    "extract_columns_from_filters_cached",
    "purge_old_logs",
]

logger = get_logger(__name__)


def _align(a: pd.Series, b: pd.Series) -> tuple[pd.Series, pd.Series]:
    """Return the pair aligned to their intersection index."""

    x, y = a.align(b, join="inner")
    return x, y


def crosses_above(a: pd.Series, b: pd.Series) -> pd.Series:
    """Return ``True`` where ``a`` crosses above ``b``."""

    if a is None or b is None:
        return pd.Series(False, index=[])
    x, y = _align(a, b)
    return (x.shift(1) < y.shift(1)) & (x >= y)


def crosses_below(a: pd.Series, b: pd.Series) -> pd.Series:
    """Return ``True`` where ``a`` crosses below ``b``."""

    if a is None or b is None:
        return pd.Series(False, index=[])
    x, y = _align(a, b)
    return (x.shift(1) > y.shift(1)) & (x <= y)




def extract_columns_from_filters(
    df_filters: pd.DataFrame | None,
    series_series: list | None,
    series_value: list | None,
) -> set:
    """Filtre sorgularında ve crossover tanımlarında geçen kolon adlarını döndürür."""
    try:
        from filter_engine import _extract_query_columns
    except Exception:
        # filter_engine import edilemezse boş set döndür
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
    """Cacheable wrapper for ``extract_columns_from_filters``.

    Parameters
    ----------
    df_filters_csv : str
        CSV representation of the filters DataFrame.
    series_series : list | None
        Definitions for series/series crossovers.
    series_value : list | None
        Definitions for series/value crossovers.
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


def purge_old_logs(dir_path: str = "loglar", days: int = 7, dry_run: bool = False):
    """Delete ``*.log`` and ``*.lock`` files older than ``days``.

    Parameters match the legacy helper for backward compatibility.
    """

    from .purge_old_logs import purge_old_logs as _impl

    return _impl(log_dir=Path(dir_path), keep_days=days, dry_run=dry_run)
