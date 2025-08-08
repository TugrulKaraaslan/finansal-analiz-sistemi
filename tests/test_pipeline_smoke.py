# DÜZENLENDİ – SYNTAX TEMİZLİĞİ
from __future__ import annotations

import pandas as pd

from backtest.backtester import run_1g_returns
from backtest.screener import run_screener


def test_pipeline_smoke():
    df = pd.DataFrame(
        {
            "symbol": ["AAA", "AAA"],
            "date": pd.to_datetime(["2024-01-05", "2024-01-06"]).normalize(),
            "close": [10.0, 11.0],
            "open": [10.0, 11.0],
            "high": [10.0, 11.0],
            "low": [10.0, 11.0],
            "volume": [100, 120],
            "rsi_14": [70, 65],
            "relative_volume": [1.2, 0.9],
        }
    )
    assert isinstance(df.loc[0, "date"], pd.Timestamp)
    filters = pd.DataFrame(
        {
            "FilterCode": ["T1"],
            "PythonQuery": ["(rsi_14 > 65) and (relative_volume > 1.0)"],
        }
    )
    sigs = run_screener(df, filters, "2024-01-05")
    assert isinstance(sigs.loc[0, "Date"], pd.Timestamp)
    out = run_1g_returns(df, sigs)
    assert not out.empty
    assert isinstance(out.loc[0, "Date"], pd.Timestamp)


def test_pipeline_no_signals():
    df = pd.DataFrame(
        {
            "symbol": ["AAA", "AAA"],
            "date": pd.to_datetime(["2024-01-05", "2024-01-06"]).normalize(),
            "close": [10.0, 11.0],
            "open": [10.0, 11.0],
            "high": [10.0, 11.0],
            "low": [10.0, 11.0],
            "volume": [100, 100],
            "rsi_14": [60, 60],
            "relative_volume": [0.9, 0.9],
        }
    )
    assert isinstance(df.loc[0, "date"], pd.Timestamp)
    filters = pd.DataFrame(
        {
            "FilterCode": ["T1"],
            "PythonQuery": ["(rsi_14 > 65) and (relative_volume > 1.0)"],
        }
    )
    sigs = run_screener(df, filters, "2024-01-05")
    out = run_1g_returns(df, sigs)
    assert out.empty
    assert list(out.columns) == [
        "FilterCode",
        "Symbol",
        "Date",
        "EntryClose",
        "ExitClose",
        "ReturnPct",
        "Win",
        "Reason",
    ]
