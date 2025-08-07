import pandas as pd
import pytest

from backtest.query_parser import SafeQuery


def test_filter_returns_subset():
    df = pd.DataFrame({"x": [1, 2, 3]})
    q = SafeQuery("x > 1")
    out = q.filter(df)
    assert out["x"].tolist() == [2, 3]


def test_filter_rejects_unsafe_expression():
    df = pd.DataFrame({"x": [1, 2, 3]})
    q = SafeQuery("__import__('os').system('echo 1')")
    with pytest.raises(ValueError):
        q.filter(df)
