# DÜZENLENDİ – SYNTAX TEMİZLİĞİ
from __future__ import annotations

import pandas as pd
import pytest

from backtest.backtester import run_1g_returns


def test_backtester_basic():
    df = pd.DataFrame(
        {
            "symbol": ["AAA", "AAA"],
            "date": pd.to_datetime(["2024-01-05", "2024-01-06"]),
            "close": [10.0, 11.0],
        }
    )
    sigs = pd.DataFrame(
        {
            "FilterCode": ["T1"],
            "Symbol": ["AAA"],
            "Date": [pd.to_datetime("2024-01-05")],
        }
    )
    out = run_1g_returns(df, sigs)
    assert pytest.approx(out.loc[0, "ReturnPct"], 0.01) == 10.0


def test_run_1g_returns_drops_duplicates():
    df = pd.DataFrame(
        {
            "symbol": ["AAA", "AAA", "AAA"],
            "date": pd.to_datetime(["2024-01-05", "2024-01-05", "2024-01-06"]),
            "close": [10.0, 10.0, 11.0],
        }
    )
    sigs = pd.DataFrame(
        {
            "FilterCode": ["T1", "T1"],
            "Symbol": ["AAA", "AAA"],
            "Date": [pd.to_datetime("2024-01-05"), pd.to_datetime("2024-01-05")],
        }
    )
    out = run_1g_returns(df, sigs)
    assert len(out) == 1


def test_run_1g_returns_holding_period_and_cost():
    df = pd.DataFrame(
        {
            "symbol": ["AAA", "AAA", "AAA"],
            "date": pd.to_datetime(["2024-01-01", "2024-01-02", "2024-01-03"]),
            "close": [10.0, 11.0, 12.0],
        }
    )
    sigs = pd.DataFrame(
        {
            "FilterCode": ["T1"],
            "Symbol": ["AAA"],
            "Date": [pd.to_datetime("2024-01-01")],
        }
    )
    out = run_1g_returns(df, sigs, holding_period=2, transaction_cost=1.0)
    expected = ((12.0 / 10.0 - 1.0) * 100.0) - 1.0
    assert pytest.approx(out.loc[0, "ReturnPct"], 0.01) == expected


def test_run_1g_returns_exit_date_out_of_bounds_returns_empty():
    df = pd.DataFrame(
        {
            "symbol": ["AAA", "AAA"],
            "date": pd.to_datetime(["2024-01-01", "2024-01-02"]),
            "close": [10.0, 11.0],
        }
    )
    sigs = pd.DataFrame(
        {
            "FilterCode": ["T1"],
            "Symbol": ["AAA"],
            "Date": [pd.to_datetime("2024-01-02")],
        }
    )
    out = run_1g_returns(df, sigs)
    assert out.empty


def test_run_1g_returns_ignores_out_of_bounds_signals():
    df = pd.DataFrame(
        {
            "symbol": ["AAA", "AAA", "AAA"],
            "date": pd.to_datetime(["2024-01-01", "2024-01-02", "2024-01-03"]),
            "close": [10.0, 11.0, 12.0],
        }
    )
    sigs = pd.DataFrame(
        {
            "FilterCode": ["T1", "T1"],
            "Symbol": ["AAA", "AAA"],
            "Date": [pd.to_datetime("2024-01-01"), pd.to_datetime("2024-01-03")],
        }
    )
    out = run_1g_returns(df, sigs)
    assert len(out) == 1
    assert out.loc[0, "Date"] == pd.Timestamp("2024-01-01")


def test_run_1g_returns_side_validation():
    df = pd.DataFrame(
        {
            "symbol": ["AAA", "AAA"],
            "date": pd.to_datetime(["2024-01-05", "2024-01-06"]),
            "close": [10.0, 11.0],
        }
    )
    sigs = pd.DataFrame(
        {
            "FilterCode": ["T1"],
            "Symbol": ["AAA"],
            "Date": [pd.to_datetime("2024-01-05")],
            "Side": ["short"],
        }
    )
    out = run_1g_returns(df, sigs)
    assert out.loc[0, "Side"] == "short"
    assert pytest.approx(out.loc[0, "ReturnPct"], 0.01) == -10.0
    sigs_bad = sigs.copy()
    sigs_bad["Side"] = ["foo"]
    with pytest.raises(ValueError):
        run_1g_returns(df, sigs_bad)


def test_run_1g_returns_fills_missing_exit_data():
    df = pd.DataFrame(
        {
            "symbol": ["AAA", "AAA", "AAA"],
            "date": pd.to_datetime(["2024-01-05", "2024-01-08", "2024-01-09"]),
            "close": [10.0, 11.0, 12.0],
        }
    )
    sigs = pd.DataFrame(
        {
            "FilterCode": ["T1"],
            "Symbol": ["AAA"],
            "Date": [pd.to_datetime("2024-01-05")],
        }
    )
    out1 = run_1g_returns(df, sigs)
    assert out1.loc[0, "ExitClose"] == 11.0
    assert pytest.approx(out1.loc[0, "ReturnPct"], 0.01) == 10.0
    out2 = run_1g_returns(df, sigs, holding_period=2)
    assert out2.loc[0, "ExitClose"] == 12.0
    assert pytest.approx(out2.loc[0, "ReturnPct"], 0.01) == 20.0
