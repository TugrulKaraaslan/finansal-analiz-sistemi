import time

import pandas as pd

from backtest.backtester import run_1g_returns
from backtest.indicators import compute_indicators


def _sample_df(n: int = 1000) -> pd.DataFrame:
    dates = pd.date_range("2024-01-01", periods=n, freq="D")
    return pd.DataFrame(
        {
            "symbol": ["AAA"] * n,
            "date": dates,
            "close": range(1, n + 1),
            "volume": range(1, n + 1),
        }
    )


def test_compute_indicators_perf():
    df = _sample_df()
    start = time.perf_counter()
    compute_indicators(df, params={}, engine="builtin")
    elapsed = time.perf_counter() - start
    assert elapsed < 1.0


def test_run_1g_returns_perf():
    df = _sample_df()
    df["next_close"] = df["close"]
    df["next_date"] = df["date"]
    sigs = pd.DataFrame(
        {"FilterCode": ["F"], "Symbol": ["AAA"], "Date": [df["date"].iloc[0]]}
    )
    start = time.perf_counter()
    run_1g_returns(df, sigs, holding_period=1, transaction_cost=0.0)
    elapsed = time.perf_counter() - start
    assert elapsed < 1.0
