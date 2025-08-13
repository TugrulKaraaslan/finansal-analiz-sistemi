import logging

import pandas as pd

from backtest.indicators import _safe_alias, compute_indicators


def test_existing_relative_volume_preserved():
    df = pd.DataFrame(
        {
            "symbol": ["AAA"] * 3,
            "date": pd.date_range("2024-01-01", periods=3, freq="D"),
            "close": [1, 2, 3],
            "volume": [1, 2, 3],
            "relative_volume": [9, 9, 9],
        }
    )
    res = compute_indicators(df, params={}, engine="builtin")
    assert "RELATIVE_VOLUME" not in res.columns
    assert "hacim_goreli" not in res.columns
    pd.testing.assert_series_equal(
        res["relative_volume"].reset_index(drop=True),
        pd.Series([9, 9, 9]),
        check_names=False,
    )


def test_safe_alias_dataframe_base(caplog):
    df = pd.DataFrame([[1, 2], [3, 4]], columns=["base", "base"])
    with caplog.at_level(logging.WARNING, logger="backtest.indicators"):
        added = _safe_alias(df, "alias", "base")
    assert not added
    assert "alias skipped" in caplog.text
    assert "alias" not in df.columns


def test_duplicate_columns_dropped(caplog):
    df = pd.DataFrame(
        {
            "symbol": ["AAA"] * 2,
            "date": pd.date_range("2024-01-01", periods=2, freq="D"),
            "close": [1, 2],
            "volume": [1, 2],
            "Change 1D Percent": [5.0, 6.0],
        }
    )
    with caplog.at_level(logging.INFO, logger="backtest.indicators"):
        res = compute_indicators(df, params={}, engine="builtin")
    assert res.columns.tolist().count("change_1d_percent") == 1
    assert "duplicate columns dropped" in caplog.text


def test_pandas_ta_missing(monkeypatch, caplog):
    df = pd.DataFrame(
        {
            "symbol": ["AAA"] * 3,
            "date": pd.date_range("2024-01-01", periods=3, freq="D"),
            "close": [1, 2, 3],
            "volume": [1, 2, 3],
        }
    )
    monkeypatch.setattr("backtest.indicators.ta", None, raising=False)
    with caplog.at_level(logging.WARNING, logger="backtest.indicators"):
        res = compute_indicators(df, params={}, engine="pandas_ta")
    assert "pandas_ta bulunamadı" in caplog.text
    assert "EMA_10" in res.columns
