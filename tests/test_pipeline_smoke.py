# DÜZENLENDİ – SYNTAX TEMİZLİĞİ
from __future__ import annotations

import pandas as pd

from backtest.backtester import run_1g_returns
from backtest.screener import run_screener


def test_pipeline_smoke():
    df = pd.DataFrame(
        {
            "symbol": ["AAA", "AAA"],
            "date": pd.to_datetime(["2024-01-05", "2024-01-08"]).normalize(),
            "close": [10.0, 11.0],
            "next_close": [11.0, None],
            "next_date": pd.to_datetime(["2024-01-08", "2024-01-09"]).normalize(),
            "open": [10.0, 11.0],
            "high": [10.0, 11.0],
            "low": [10.0, 11.0],
            "volume": [100, 120],
            "rsi_14": [70, 65],
            "relative_volume": [1.2, 0.9],
        }
    )
    filters = pd.DataFrame(
        {
            "FilterCode": ["T1"],
            "PythonQuery": ["(rsi_14 > 65) and (relative_volume > 1.0)"],
        }
    )
    sigs = run_screener(df, filters, "2024-01-05")
    out = run_1g_returns(df, sigs)
    assert not out.empty


def test_pipeline_no_signals():
    df = pd.DataFrame(
        {
            "symbol": ["AAA"],
            "date": pd.to_datetime(["2024-01-05"]).normalize(),
            "close": [10.0],
            "next_close": [11.0],
            "next_date": pd.to_datetime(["2024-01-08"]).normalize(),
            "open": [10.0],
            "high": [10.0],
            "low": [10.0],
            "volume": [100],
            "rsi_14": [60],
            "relative_volume": [0.9],
        }
    )
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
    ]
