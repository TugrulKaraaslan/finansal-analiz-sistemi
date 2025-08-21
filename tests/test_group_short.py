import pandas as pd
import pytest

from backtest.backtester import run_1g_returns
from backtest.calendars import add_next_close_calendar, build_trading_days
from backtest.screener import run_screener


def test_run_screener_includes_group():
    df = pd.DataFrame(
        {
            "symbol": ["AAA"],
            "date": pd.to_datetime(["2024-01-02"]).normalize(),
            "open": [1.0],
            "high": [1.0],
            "low": [1.0],
            "close": [1.0],
            "volume": [100],
        }
    )
    filters_df = pd.DataFrame(
        {"FilterCode": ["F1"], "PythonQuery": ["close > 0"], "Group": ["G1"]}
    )
    res = run_screener(df, filters_df, pd.Timestamp("2024-01-02"))
    assert "Group" in res.columns
    assert res.loc[0, "Group"] == "G1"


def test_run_1g_returns_handles_short_and_group():
    df = pd.DataFrame(
        {
            "symbol": ["AAA", "AAA"],
            "date": pd.to_datetime(["2024-01-05", "2024-01-08"]).normalize(),
            "close": [10.0, 11.0],
        }
    )
    tdays = build_trading_days(df)
    df = add_next_close_calendar(df, tdays)
    signals = pd.DataFrame(
        {
            "FilterCode": ["F1", "F1"],
            "Group": ["G1", "G1"],
            "Symbol": ["AAA", "AAA"],
            "Date": [pd.Timestamp("2024-01-05"), pd.Timestamp("2024-01-05")],
            "Side": ["long", "short"],
        }
    )
    out = run_1g_returns(df, signals, trading_days=tdays)
    assert set(["Group", "Side"]).issubset(out.columns)
    assert out["Reason"].isna().all()
    long_ret = (11.0 / 10.0 - 1.0) * 100.0
    short_ret = ((10.0 - 11.0) / 10.0) * 100.0
    assert (
        pytest.approx(out[out["Side"] == "long"]["ReturnPct"].iloc[0], 0.01) == long_ret
    )
    assert (
        pytest.approx(out[out["Side"] == "short"]["ReturnPct"].iloc[0], 0.01)
        == short_ret
    )
