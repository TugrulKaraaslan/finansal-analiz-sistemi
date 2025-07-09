"""Unit tests for backtest_core_param."""

import warnings

import numpy as np
import pandas as pd
import pytest

warnings.filterwarnings(
    "ignore",
    message=".*swapaxes.*will change in a future version of pandas",
    category=FutureWarning,
)

try:
    import backtest_core as bc
except Exception:
    pytest.skip("backtest_core module not found", allow_module_level=True)

DF = pd.DataFrame(
    {
        "hisse_kodu": ["AAA", "AAA"],
        "tarih": [
            pd.to_datetime("09.03.2025", dayfirst=True),
            pd.to_datetime("11.03.2025", dayfirst=True),
        ],
        "close": [10.0, 11.0],
    }
)


def test_get_fiyat_non_numeric():
    """Return ``NaN`` when price column contains non-numeric data."""
    df = DF.copy()
    df.loc[0, "close"] = np.nan  # avoids object→float warning
    out = bc._get_fiyat(df, df.loc[0, "tarih"], "close")
    assert np.isnan(out)


@pytest.mark.parametrize(
    "tarih,col,expected",
    [
        (pd.to_datetime("09.03.2025", dayfirst=True), "close", 10.0),
        (pd.to_datetime("10.03.2025", dayfirst=True), "close", 11.0),
        (pd.to_datetime("12.03.2025", dayfirst=True), "close", 11.0),
        (pd.to_datetime("09.03.2025", dayfirst=True), "open", np.nan),
    ],
)
def test_get_fiyat_param(tarih, col, expected):
    """Return expected value when the price is present."""
    out = bc._get_fiyat(DF.copy(), tarih, col)
    if np.isnan(expected):
        assert np.isnan(out)
    else:
        assert out == expected


def test_get_fiyat_string_dates():
    """Handle date strings when locating the target price."""
    df = pd.DataFrame(
        {
            "hisse_kodu": ["AAA", "AAA"],
            "tarih": ["09.03.2025", "11.03.2025"],
            "close": [10.0, 11.0],
        }
    )
    out = bc._get_fiyat(df, pd.to_datetime("10.03.2025", dayfirst=True), "close")
    assert out == 11.0
