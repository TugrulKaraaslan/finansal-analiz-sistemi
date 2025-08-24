import numpy as np
import pandas as pd

from backtest.eval.metrics import rolling_future_return


def test_rolling_forward_nan_tail():
    s = pd.Series([100, 101, 102, 103])
    f = rolling_future_return(s, 2)
    assert f.iloc[-2:].isna().all()
