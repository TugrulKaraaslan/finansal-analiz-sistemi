import pandas as pd

from backtest.filters.engine import evaluate


def _df():
    return pd.DataFrame({"close": [1, 2, 3]})


def test_true_literal_all_true():
    df = _df()
    out = evaluate(df, "true")
    assert out.tolist() == [True, True, True]


def test_false_literal_all_false():
    df = _df()
    out = evaluate(df, "false")
    assert out.tolist() == [False, False, False]


def test_mixed_expression_and_true():
    df = _df()
    out1 = evaluate(df, "close > 0 and true")
    out2 = evaluate(df, "close > 0")
    assert out1.equals(out2)


def test_case_variants():
    df = _df()
    out = evaluate(df, "True and not FALSE")
    assert out.tolist() == [True, True, True]

