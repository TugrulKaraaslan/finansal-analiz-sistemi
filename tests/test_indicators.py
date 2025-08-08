import numpy as np
import pandas as pd
import pytest

import indicator_calculator as ic


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
