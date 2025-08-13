import io
import numpy as np
import pandas as pd
import pytest

import indicator_calculator as ic
from backtest.indicators import _safe_alias, compute_indicators
from loguru import logger


def test_indicator_calculator_outputs():
    df = pd.read_csv('tests/data/indicator_sample.csv')

    sma = ic.sma_5(df['close'])
    ema = ic.ema_13(df['close'])
    adx = ic.adx_14(df['high'], df['low'], df['close'])

    expected_sma = pd.Series([np.nan, np.nan, np.nan, np.nan, 12.0, 13.0, 14.0, 15.0, 16.0, 17.0])
    pd.testing.assert_series_equal(sma, expected_sma, check_names=False)

    expected_ema = pd.Series([
        10.0,
        10.142857,
        10.408163,
        10.778426,
        11.238651,
        11.775986,
        12.379417,
        13.039500,
        13.748143,
        14.498408,
    ])
    np.testing.assert_allclose(ema.values, expected_ema.values, rtol=1e-6, atol=1e-6)

    close = pd.Series([44,47,52,48,44,46,50,49,48,47,49,53,54,56,58,57,55], dtype=float)
    rsi = ic.rsi_14(close)
    expected_rsi = pd.Series(
        [np.nan]*14 + [84.577233, 82.142390, 77.346463]
    )
    pd.testing.assert_series_equal(rsi.reset_index(drop=True), expected_rsi, check_names=False)

    assert adx.isna().all()


def test_adx_without_pandas_ta(monkeypatch):
    monkeypatch.setattr(ic, "ta", None)
    with pytest.warns(RuntimeWarning):
        out = ic.adx_14(pd.Series([1, 2]), pd.Series([1, 2]), pd.Series([1, 2]))
    assert out.isna().all()


def test_existing_relative_volume_preserved():
    df = pd.DataFrame(
        {
            "symbol": ["AAA"] * 3,
            "date": pd.date_range("2024-01-01", periods=3, freq="D"),
            "close": [1, 2, 3],
            "volume": [1, 2, 3],
            "relative_volume": [9, 9, 9],
        }
    )
    res = compute_indicators(df, params={}, engine="builtin")
    assert "RELATIVE_VOLUME" not in res.columns
    assert "hacim_goreli" not in res.columns
    pd.testing.assert_series_equal(
        res["relative_volume"].reset_index(drop=True),
        pd.Series([9, 9, 9]),
        check_names=False,
    )


def test_safe_alias_dataframe_base():
    df = pd.DataFrame([[1, 2], [3, 4]], columns=["base", "base"])
    buf = io.StringIO()
    h = logger.add(buf, level="WARNING")
    try:
        added = _safe_alias(df, "alias", "base")
    finally:
        logger.remove(h)
    assert not added
    assert "alias skipped" in buf.getvalue()
    assert "alias" not in df.columns


def test_duplicate_columns_dropped():
    df = pd.DataFrame(
        {
            "symbol": ["AAA"] * 2,
            "date": pd.date_range("2024-01-01", periods=2, freq="D"),
            "close": [1, 2],
            "volume": [1, 2],
            "Change 1D Percent": [5.0, 6.0],
        }
    )
    buf = io.StringIO()
    h = logger.add(buf, level="INFO")
    try:
        res = compute_indicators(df, params={}, engine="builtin")
    finally:
        logger.remove(h)
    assert res.columns.tolist().count("change_1d_percent") == 1
    assert "duplicate columns dropped" in buf.getvalue()
