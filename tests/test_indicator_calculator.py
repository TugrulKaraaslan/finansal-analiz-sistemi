"""Test module for test_indicator_calculator."""

import os
import sys
import warnings

import numpy as np
import pandas as pd
import pytest

ta = pytest.importorskip("pandas_ta")
if not hasattr(ta, "psar"):
    pytest.skip("psar not available", allow_module_level=True)

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.modules.pop("pandas_ta", None)  # Ensure real pandas_ta is used in this test

import indicator_calculator as ic  # noqa: E402
from finansal_analiz_sistemi import config  # noqa: E402


def test_classicpivots_crossover_column_exists():
    """Test test_classicpivots_crossover_column_exists."""
    data = {
        "hisse_kodu": ["AAA"] * 30,
        "tarih": pd.date_range("2024-01-01", periods=30, freq="D"),
        "open": np.linspace(1, 30, 30),
        "high": np.linspace(1, 30, 30) + 1,
        "low": np.linspace(1, 30, 30) - 1,
        "close": np.linspace(1, 30, 30),
        "volume": np.arange(30),
    }
    df = pd.DataFrame(data)
    with warnings.catch_warnings(record=True) as rec:
        warnings.simplefilter("error")
        result = ic.hesapla_teknik_indikatorler_ve_kesisimler(df)
        assert not rec
    assert not any("fragmented" in str(w.message) for w in rec)
    assert "classicpivots_1h_p" in result.columns
    assert "close_keser_classicpivots_1h_p_yukari" in result.columns


def test_fallback_indicators_created_when_missing():
    """Test test_fallback_indicators_created_when_missing."""
    data = {
        "hisse_kodu": ["AAA"] * 50,
        "tarih": pd.date_range("2024-01-01", periods=50, freq="D"),
        "open": np.linspace(1, 50, 50),
        "high": np.linspace(1, 50, 50) + 1,
        "low": np.linspace(1, 50, 50) - 1,
        "close": np.linspace(1, 50, 50),
        "volume": np.arange(50),
    }
    df = pd.DataFrame(data)
    with warnings.catch_warnings(record=True) as rec:
        warnings.simplefilter("error")
        result = ic.hesapla_teknik_indikatorler_ve_kesisimler(df)
        assert not rec
    assert not any("fragmented" in str(w.message) for w in rec)
    # pandas_ta normalde sma_200/ema_200 üretmez.
    # Fallback mekanizmasi kolonlarin NaN dahi olsa eklenmesini saglar.
    assert "sma_200" in result.columns
    assert "ema_200" in result.columns
    assert "momentum_10" in result.columns
    assert "tema_20" in result.columns


@pytest.mark.parametrize("bars", [30, 60, 252])
def test_ma_columns_exist_for_various_lengths(bars):
    """Test test_ma_columns_exist_for_various_lengths."""
    data = {
        "hisse_kodu": ["AAA"] * bars,
        "tarih": pd.date_range("2024-01-01", periods=bars, freq="D"),
        "open": np.linspace(1, bars, bars),
        "high": np.linspace(1, bars, bars) + 1,
        "low": np.linspace(1, bars, bars) - 1,
        "close": np.linspace(1, bars, bars),
        "volume": np.arange(bars),
    }
    df = pd.DataFrame(data)
    with warnings.catch_warnings(record=True) as rec:
        warnings.simplefilter("error")
        result = ic.hesapla_teknik_indikatorler_ve_kesisimler(df)
        assert not rec
    assert not any("fragmented" in str(w.message) for w in rec)
    for n in config.GEREKLI_MA_PERIYOTLAR:
        assert f"sma_{n}" in result.columns
        assert f"ema_{n}" in result.columns


def test_crossover_skips_when_column_missing():
    """Test test_crossover_skips_when_column_missing."""
    data = {
        "hisse_kodu": ["AAA"] * 5,
        "tarih": pd.date_range("2024-01-01", periods=5, freq="D"),
        "ema_20": np.arange(5, 10),
    }
    df = pd.DataFrame(data)
    result = ic._calculate_series_series_crossover(
        df,
        "ema_10",
        "ema_20",
        "ema_10_keser_ema_20_yukari",
        "ema_10_keser_ema_20_asagi",
    )
    assert result is None


def test_core_strategy_indicators_exist():
    """Test test_core_strategy_indicators_exist."""
    df = pd.DataFrame(
        {
            "hisse_kodu": ["AAA"] * 60,
            "tarih": pd.date_range("2024-01-01", periods=60, freq="D"),
            "open": np.linspace(1, 60, 60),
            "high": np.linspace(1, 60, 60) + 1,
            "low": np.linspace(1, 60, 60) - 1,
            "close": np.linspace(1, 60, 60),
            "volume": np.arange(60),
        }
    )
    result = ic.hesapla_teknik_indikatorler_ve_kesisimler(df)
    for col in [
        "rsi_14",
        "macd_line",
        "macd_signal",
        "ichimoku_conversionline",
    ]:
        assert col in result.columns
        assert result[col].notna().any()
