"""Test module for test_backtest_core_extra."""

import os
import sys
import types

import numpy as np
import pandas as pd

sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
)  # isort: off

import backtest_core  # noqa: E402

sys.modules.setdefault("pandas_ta", types.SimpleNamespace(Strategy=lambda **kw: None))


def test_get_fiyat_no_data_nearby():
    """Test test_get_fiyat_no_data_nearby."""
    df = pd.DataFrame({"hisse_kodu": [], "tarih": [], "close": []})
    out = backtest_core._get_fiyat(
        df, pd.to_datetime("01.03.2025", dayfirst=True), "close"
    )
    assert np.isnan(out)


def test_get_fiyat_invalid_value():
    """Test test_get_fiyat_invalid_value."""
    df = pd.DataFrame(
        {
            "hisse_kodu": ["AAA"],
            "tarih": [pd.to_datetime("07.03.2025", dayfirst=True)],
            "close": ["abc"],
        }
    )
    out = backtest_core._get_fiyat(
        df, pd.to_datetime("07.03.2025", dayfirst=True), "close"
    )
    assert np.isnan(out)


def test_backtest_empty_data():
    """Test test_backtest_empty_data."""
    rapor_df, detay_df = backtest_core.calistir_basit_backtest(
        {"F1": {"hisseler": [], "sebep": "OK", "hisse_sayisi": 0}},
        pd.DataFrame(),
        "10.03.2025",
        "07.03.2025",
    )
    assert rapor_df.empty and detay_df.empty


def test_backtest_invalid_dates():
    """Test test_backtest_invalid_dates."""
    df = pd.DataFrame(
        {
            "hisse_kodu": ["AAA"],
            "tarih": [pd.to_datetime("07.03.2025", dayfirst=True)],
            "close": [12.5],
        }
    )
    rapor_df, detay_df = backtest_core.calistir_basit_backtest(
        {}, df, "2025/03/10", "2025/03/07"
    )
    assert rapor_df.empty and detay_df.empty
