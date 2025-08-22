import pandas as pd
import pytest

from backtest.pipeline.precompute import precompute_needed


@pytest.mark.parametrize("rewrite", [0, 1])
def test_precompute_lag(monkeypatch, rewrite):
    if rewrite:
        monkeypatch.setenv("CROSS_REWRITE", "1")
    else:
        monkeypatch.delenv("CROSS_REWRITE", raising=False)

    df = pd.DataFrame({"a": [1, 2, 3], "b": [3, 2, 1]})
    exprs = ["crossup(a, b)", "crossdown(a, b)"]
    df2 = precompute_needed(df.copy(), exprs)
    assert "lag1__a" in df2.columns and "lag1__b" in df2.columns
    pd.testing.assert_series_equal(
        df2["lag1__a"],
        df["a"].shift(1),
        check_names=False,
    )
    pd.testing.assert_series_equal(
        df2["lag1__b"],
        df["b"].shift(1),
        check_names=False,
    )
