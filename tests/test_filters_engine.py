import pandas as pd
from backtest.filters.engine import evaluate


def _df():
    return pd.DataFrame(
        {
            "ichimoku_conversionline": pd.Series([1, 2, 3]),
            "ichimoku_baseline": pd.Series([1, 1, 4]),
            "macd_line": pd.Series([0.1, -0.2, 0.3]),
            "macd_signal": pd.Series([0.0, 0.0, 0.0]),
        }
    )


def test_alias_macd():
    df = _df()
    s = evaluate(df, "MACD_line > macd-signal")
    assert s.dtype == "bool"


def test_macd_names():
    df = _df()
    s = evaluate(df, "macd_line > macd_signal")
    assert s.tolist() == [True, False, True]
