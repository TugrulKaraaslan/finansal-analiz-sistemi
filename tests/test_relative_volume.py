import numpy as np
import pandas as pd
import pytest

from backtest.indicators import compute_indicators


def test_relative_volume_no_nan_and_no_div_zero():
    df = pd.DataFrame(
        {
            "symbol": ["AAA"] * 5,
            "date": pd.date_range("2024-01-01", periods=5, freq="D"),
            "close": [10, 11, 12, 13, 14],
            "open": [10, 11, 12, 13, 14],
            "high": [10, 11, 12, 13, 14],
            "low": [10, 11, 12, 13, 14],
            "volume": [0, 100, 110, 120, 130],
        }
    )
    res = compute_indicators(df)
    rv = res["relative_volume"]
    assert rv.notna().all()
    assert not np.isinf(rv).any()
    assert rv.iloc[0] == 0
    assert rv.iloc[1] == pytest.approx(2.0)
