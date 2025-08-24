import numpy as np
import pandas as pd

from backtest.engine.exec import apply_t_plus_one


def test_t_plus_one_exec():
    sig = pd.Series([1, 0, 1], index=pd.date_range("2020-01-01", periods=3))
    out = apply_t_plus_one(sig)
    assert np.isnan(out.iloc[0])
    assert out.iloc[1] == 1
