import pandas as pd
from backtest.pipeline.precompute import precompute_needed


def test_precompute_no_lag():
    df = pd.DataFrame({"a": [1, 2, 3], "b": [3, 2, 1]})
    df2 = precompute_needed(df.copy(), {"a", "b"})
    assert "lag1__a" not in df2.columns
    assert "lag1__b" not in df2.columns
