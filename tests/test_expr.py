import pandas as pd
from loguru import logger

from backtest.expr import evaluate


def test_crossup():
    df = pd.DataFrame({"a": [1, 2, 3], "b": [3, 2, 1]})
    mask = evaluate(df, "CROSSUP(a, b)")
    assert mask.tolist() == [False, False, True]


def test_crossdown():
    df = pd.DataFrame({"a": [3, 2, 1], "b": [1, 2, 3]})
    mask = evaluate(df, "CROSSDOWN(a, b)")
    assert mask.tolist() == [False, False, True]


def test_cross_up_alias():
    df = pd.DataFrame({"a": [1, 2, 3], "b": [3, 2, 1]})
    mask = evaluate(df, "cross_up(a, b)")
    assert mask.tolist() == [False, False, True]


def test_operators_series_series():
    df = pd.DataFrame({"ema_10": [1, 3, 2], "close": [2, 1, 2]})
    mask = evaluate(df, "EMA_10 > close")
    expected = df["ema_10"] > df["close"]
    assert mask.equals(expected)


def test_operator_series_constant():
    df = pd.DataFrame({"rsi_14": [45, 55, 50]})
    mask = evaluate(df, "RSI_14 >= 50")
    expected = df["rsi_14"] >= 50
    assert mask.equals(expected)


def test_intraday_column_skipped(caplog):
    df = pd.DataFrame({"change_1h_percent": [-1, 2, 3]})
    logger.add(caplog.handler, level="WARNING")
    mask = evaluate(df, "change_1h_percent > 0")
    assert mask.tolist() == [True, True, True]
    assert "intraday filtre çıkarıldı" in caplog.text
