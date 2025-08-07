import pandas as pd

from backtest.query_parser import SafeQuery
from backtest.screener import run_screener


def test_safequery_basic():
    q = SafeQuery("rsi_14 > 70 & close>ema_20")
    assert q.is_safe


def test_safequery_rejects_calls_and_attributes():
    assert not SafeQuery("__import__('os').system('echo 1')").is_safe
    assert not SafeQuery("df.__class__").is_safe


def test_run_screener_skips_unsafe():
    df_ind = pd.DataFrame(
        {
            "symbol": ["AAA"],
            "date": pd.to_datetime(["2024-01-02"]).date,
            "open": [1.0],
            "high": [1.0],
            "low": [1.0],
            "close": [1.0],
            "volume": [100],
        }
    )
    filters = pd.DataFrame(
        {
            "FilterCode": ["SAFE", "BAD"],
            "PythonQuery": ["close > 0", "__import__('os').system('echo 1')"],
        }
    )
    res = run_screener(df_ind, filters, pd.Timestamp("2024-01-02"))
    assert res["FilterCode"].tolist() == ["SAFE"]
