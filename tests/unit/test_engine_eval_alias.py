import pandas as pd
import pytest

from backtest.filters.engine import evaluate


def _sample_df():
    return pd.DataFrame(
        {
            "ichimoku_conversionline": [0, 1, 2],
            "ichimoku_baseline": [0, 1, 2],
            "macd_line": [0.1, 0.2, 0.3],
            "macd_signal": [0.0, 0.0, 0.0],
            "bbm_20_2": [1, 1, 1],
            "bbu_20_2": [2, 2, 2],
            "bbl_20_2": [0, 0, 0],
            "Close": [10, 11, 12],
        }
    )


def test_alias_evaluation_warning_and_result():
    df = _sample_df()
    with pytest.warns(UserWarning):
        res_alias = evaluate(df, "its_9 > 0")
    res_canon = evaluate(df, "ichimoku_conversionline > 0")
    assert res_alias.equals(res_canon)


def test_lowercase_columns_and_spaced_alias():
    df = _sample_df()
    assert evaluate(df, "close > 0").all()
    with pytest.warns(UserWarning):
        res_space = evaluate(df, "bbm_20 2 > 0")
    res_canon = evaluate(df, "bbm_20_2 > 0")
    assert res_space.equals(res_canon)


def test_unknown_column_raises():
    df = _sample_df()
    with pytest.raises(NameError):
        evaluate(df, "unknown_col > 0")
