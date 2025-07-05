"""Compatibility wrapper for ``finansal_analiz_sistemi.data_loader``.

Explicit imports keep flake8 happy while exposing the same public API.
"""

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
    "load_data",
    "read_prices",
    "load_filter_csv",
    "check_and_create_dirs",
    "load_excel_katalogu",
    "_standardize_date_column",
    "_standardize_ohlcv_columns",
    "yukle_filtre_dosyasi",
    "yukle_hisse_verileri",
    "load_dataset",
]


def load_dataset(rebuild: bool = False) -> pd.DataFrame:
    """Return cached stock dataset, rebuilding if requested or missing."""
    parquet_path = Path(config.PARQUET_CACHE_PATH)
    if rebuild or not parquet_path.exists():
        cache_builder.build()
    if not parquet_path.exists():
        raise FileNotFoundError(parquet_path)
    df = pd.read_parquet(parquet_path)
    if df.empty:
        raise ValueError("Parquet cache empty")
    return df
