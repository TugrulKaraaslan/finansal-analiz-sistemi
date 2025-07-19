"""Unit tests for :mod:`preprocessor`.

These tests verify numeric parsing and date handling.
"""

import os
import sys

import pandas as pd

import preprocessor
from finansal_analiz_sistemi import config

# Add the project root to ``sys.path`` for standalone execution
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


def test_temizle_sayisal_deger_thousand_comma():
    """Parse numbers with Turkish thousands separators correctly."""
    cases = {
        "1.234,56": 1234.56,
        "12.345,67": 12345.67,
        "1.234.567,89": 1234567.89,
    }
    for text, expected in cases.items():
        result = preprocessor._temizle_sayisal_deger(text)
        assert result == expected


def test_on_isle_hisse_verileri_invalid_dates_dropped_and_numeric():
    """Invalid dates are dropped and numeric columns cast to float."""
    data = {
        "hisse_kodu": ["AAA", "AAA", "AAA"],
        "tarih": ["01.03.2025", "31.02.2025", "02.03.2025"],
        "open": ["1.000,50", "1.000,50", "1.000,50"],
        "high": ["1.100,75", "1.100,75", "1.100,75"],
        "low": ["900,25", "900,25", "900,25"],
        "close": ["1.050,00", "1.050,00", "1.050,00"],
        "volume": ["1.000", "1.000", "1.000"],
    }
    df = pd.DataFrame(data)

    original_flag = config.TR_HOLIDAYS_REMOVE
    config.TR_HOLIDAYS_REMOVE = False
    try:
        result = preprocessor.on_isle_hisse_verileri(df)
    finally:
        config.TR_HOLIDAYS_REMOVE = original_flag

    assert len(result) == 2
    for col in ["open", "high", "low", "close", "volume"]:
        assert result[col].dtype == float


def test_convert_numeric_columns_converts_object_dtype(caplog):
    """Object tipindeki kolonlar floats olarak dönüştürülmeli."""
    df = pd.DataFrame({"open": ["1,00"], "foo": ["2,50"]})
    with caplog.at_level("WARNING"):
        preprocessor._convert_numeric_columns(df, ["open", "foo"])
    assert df["open"].dtype == float
    assert df["foo"].dtype == float


def test_convert_numeric_columns_warns_missing_base_col(caplog):
    """Temel kolon eksikse uyarı loglanmalı."""
    df = pd.DataFrame({"open": [1.0]})
    with caplog.at_level("WARNING"):
        preprocessor._convert_numeric_columns(df, ["open", "close"])
    assert "DataFrame'de bulunamadı" in caplog.text
