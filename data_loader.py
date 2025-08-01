"""Convenience wrappers around :mod:`finansal_analiz_sistemi.data_loader`.

Common helpers are re-exported for direct import and a helper is provided
to load the cached Parquet dataset.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

import cache_builder
from finansal_analiz_sistemi import config
from finansal_analiz_sistemi.data_loader import (
    _standardize_date_column,
    _standardize_ohlcv_columns,
    check_and_create_dirs,
    load_data,
    load_excel_katalogu,
    load_filter_csv,
    read_prices,
    yukle_filtre_dosyasi,
    yukle_hisse_verileri,
)

__all__ = [
    "_standardize_date_column",
    "_standardize_ohlcv_columns",
    "check_and_create_dirs",
    "load_data",
    "load_dataset",
    "load_excel_katalogu",
    "load_filter_csv",
    "read_prices",
    "yukle_filtre_dosyasi",
    "yukle_hisse_verileri",
]


def load_dataset(rebuild: bool = False) -> pd.DataFrame:
    """Return cached stock data, rebuilding the cache when needed.

    Args:
        rebuild (bool, optional): Force regeneration of the Parquet cache.

    Returns:
        pd.DataFrame: Combined dataset read from ``config.PARQUET_CACHE_PATH``.

    """
    parquet_path = Path(config.PARQUET_CACHE_PATH)
    if rebuild or not parquet_path.exists():
        cache_builder.build()
    if not parquet_path.exists():
        raise FileNotFoundError(parquet_path)
    df = pd.read_parquet(parquet_path)
    if df.empty:
        raise ValueError("Parquet cache empty")
    return df
