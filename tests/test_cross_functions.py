import pandas as pd
import pytest

from backtest.cross import cross_up, cross_down
from backtest.filters.engine import evaluate


@pytest.mark.parametrize("rewrite", [0, 1])
def test_crossup_crossdown(rewrite, monkeypatch):
    if rewrite:
        monkeypatch.setenv("CROSS_REWRITE", "1")
    else:
        monkeypatch.delenv("CROSS_REWRITE", raising=False)

    df_up = pd.DataFrame({"a": [1, 2, 3, 2], "b": [3, 2, 1, 2]})
    res_up = evaluate(df_up.copy(), "crossup(a, b)")
    expected_up = cross_up(df_up["a"], df_up["b"])
    pd.testing.assert_series_equal(res_up, expected_up)

    df_down = pd.DataFrame({"a": [3, 2, 1, 2], "b": [1, 2, 3, 2]})
    res_down = evaluate(df_down.copy(), "crossdown(a, b)")
    expected_down = cross_down(df_down["a"], df_down["b"])
    pd.testing.assert_series_equal(res_down, expected_down)
