import pandas as pd
import pandas_ta as ta
import indicator_calculator as ic


def test_rsi_and_adx_match_pandas_ta():
    close = pd.Series(range(1, 31))
    high = close + 1
    low = close - 1
    expected_rsi = ta.rsi(close, length=14)
    expected_adx = ta.adx(high, low, close, length=14)["ADX_14"]
    pd.testing.assert_series_equal(ic.rsi_14(close), expected_rsi, check_names=False)
    pd.testing.assert_series_equal(
        ic.adx_14(high, low, close), expected_adx, check_names=False
    )
