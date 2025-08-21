import logging

import pandas as pd

from backtest.crossovers import generate_crossovers


def test_generate_crossovers_series_and_value():
    df = pd.DataFrame(
        {
            "sma_10": [1, 2, 1, 3],
            "sma_50": [1, 1, 2, 2],
            "adx_14": [10, 30, 10, 30],
        }
    )
    res = generate_crossovers(df)
    assert list(res["sma_10_keser_sma_50_yukari"]) == [False, True, False, True]
    assert list(res["sma_10_keser_sma_50_asagi"]) == [False, False, True, False]
    assert list(res["adx_14_keser_20p0_yukari"]) == [False, True, False, True]
    assert list(res["adx_14_keser_20p0_asagi"]) == [False, False, True, False]


def test_generate_crossovers_missing_columns(caplog):
    df = pd.DataFrame({"sma_10": [1, 2, 3]})
    with caplog.at_level(logging.WARNING):
        res = generate_crossovers(df)
    assert "skip crossover: missing column(s)" in caplog.text
    assert "sma_10_keser_sma_50_yukari" not in res.columns
