# DÜZENLENDİ – SYNTAX TEMİZLİĞİ
import pandas as pd
import pytest

from backtest.backtester import run_1g_returns


def _base_df():
    return pd.DataFrame(
        {
            "symbol": ["AAA"],
            "date": pd.to_datetime(["2024-01-01"]).date,
            "close": [1.0],
            "next_date": pd.to_datetime(["2024-01-02"]).date,
            "next_close": [1.1],
        }
    )


def _signals_df():
    return pd.DataFrame(
        {
            "FilterCode": ["F"],
            "Symbol": ["AAA"],
            "Date": pd.to_datetime(["2024-01-01"]).date,
        }
    )


def test_run_1g_returns_type_validation():
    with pytest.raises(TypeError):
        run_1g_returns([], pd.DataFrame())  # type: ignore[arg-type]
    with pytest.raises(TypeError):
        run_1g_returns(_base_df(), [])  # type: ignore[arg-type]


def test_run_1g_returns_missing_columns():
    bad_df = pd.DataFrame({"symbol": ["AAA"]})
    with pytest.raises(ValueError):
        run_1g_returns(bad_df, _signals_df())
    bad_sig = pd.DataFrame({"FilterCode": ["F"], "Symbol": ["AAA"]})
    with pytest.raises(ValueError):
        run_1g_returns(_base_df(), bad_sig)


def test_run_1g_returns_empty_signals():
    res = run_1g_returns(
        _base_df(), pd.DataFrame(columns=["FilterCode", "Symbol", "Date"])
    )
    assert list(res.columns) == [
        "FilterCode",
        "Symbol",
        "Date",
        "EntryClose",
        "ExitClose",
        "ReturnPct",
        "Win",
    ]
    assert res.empty
