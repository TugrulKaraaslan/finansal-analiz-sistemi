import pandas as pd
from backtest.filters.engine import cross_up, cross_down

def test_cross_exclusive():
    a = pd.Series([0, 1, 2, 1, 0])
    b = pd.Series([1, 1, 1, 1, 1])
    up = cross_up(a, b)
    down = cross_down(a, b)
    assert not (up & down).any()
