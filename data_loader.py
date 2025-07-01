"""Compatibility wrapper for ``finansal_analiz_sistemi.data_loader``.

Explicit imports keep flake8 happy while exposing the same public API.
"""

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
]
