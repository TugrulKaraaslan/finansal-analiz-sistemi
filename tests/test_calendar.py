# DÜZENLENDİ – SYNTAX TEMİZLİĞİ
from __future__ import annotations

import pandas as pd

from backtest.calendars import (add_next_close, add_next_close_calendar,
                                build_trading_days)


def test_next_close():
    df = pd.DataFrame(
        {
            "symbol": ["AAA", "AAA", "AAA"],
            "date": pd.to_datetime(["2024-01-05", "2024-01-08", "2024-01-09"]).date,
            "close": [10, 11, 11.5],
            "open": [0, 0, 0],
            "high": [0, 0, 0],
            "low": [0, 0, 0],
            "volume": [1, 1, 1],
        }
    )
    out = add_next_close(df)
    assert out.loc[0, "next_close"] == 11
    assert pd.isna(out.loc[2, "next_close"])


def test_build_trading_days_single_holiday():
    df = pd.DataFrame({"date": pd.to_datetime(["2024-01-01", "2024-01-03"]).date})
    tdays = build_trading_days(df, pd.Timestamp("2024-01-02"))
    assert pd.Timestamp("2024-01-02") not in tdays


def test_add_next_close_calendar():
    df = pd.DataFrame(
        {
            "symbol": ["AAA", "AAA"],
            "date": pd.to_datetime(["2024-01-01", "2024-01-02"]).date,
            "close": [10.0, 11.0],
        }
    )
    tdays = build_trading_days(df)
    out = add_next_close_calendar(df, tdays)
    assert out.loc[0, "next_close"] == 11.0
    assert out.loc[0, "next_date"] == pd.Timestamp("2024-01-02").date()
