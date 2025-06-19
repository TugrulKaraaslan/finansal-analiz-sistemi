# utils.py
# -*- coding: utf-8 -*-
# Proje: Finansal Analiz ve Backtest Sistemi Geliştirme
# Modül: Yardımcı Fonksiyonlar (Örn: Kesişimler)
# Tuğrul Karaaslan & Gemini
# Tarih: 18 Mayıs 2025 (Yorumlar eklendi, NaN yönetimi teyit edildi)

import pandas as pd
from logging_config import get_logger
from utils.logging_setup import setup_logger
from functools import lru_cache
from io import StringIO

logger = get_logger(__name__)


def _align(a: pd.Series, b: pd.Series):
    x, y = a.align(b, join="inner")
    return x, y


def crosses_above(a: pd.Series, b: pd.Series) -> pd.Series:
    if a is None or b is None:
        return pd.Series(False, index=[])
    x, y = _align(a, b)
    return (x.shift(1) < y.shift(1)) & (x >= y)


def crosses_below(a: pd.Series, b: pd.Series) -> pd.Series:
    if a is None or b is None:
        return pd.Series(False, index=[])
    x, y = _align(a, b)
    return (x.shift(1) > y.shift(1)) & (x <= y)


# safe_pct_change gibi diğer yardımcı fonksiyonlar buraya eklenebilir.
# Şimdilik sadece kesişimler var.


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
            df_filters = pd.read_csv(StringIO(df_filters_csv))
        except Exception:
            df_filters = None

    return extract_columns_from_filters(df_filters, series_series, series_value)


def purge_old_logs(dir_path: str = "raporlar", days: int = 7) -> None:
    """Delete ``.log`` files older than ``days`` in ``dir_path``.

    Parameters
    ----------
    dir_path : str, optional
        Directory containing log files. Default is ``"raporlar"``.
    days : int, optional
        Files older than this number of days will be removed. Default is ``7``.
    """

    import glob
    import os
    import time

    for fp in glob.glob(f"{dir_path}/*.log"):
        if time.time() - os.path.getmtime(fp) > days * 24 * 3600:
            os.remove(fp)
