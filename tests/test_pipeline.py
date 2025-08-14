import pandas as pd
import pytest

from backtest.backtester import run_1g_returns
from backtest.indicators import compute_indicators
from backtest.screener import run_screener


def test_pipeline_end_to_end():
    raw = pd.DataFrame(
        {
            "symbol": ["AAA", "AAA", "AAA"],
            "date": pd.to_datetime(
                ["2024-01-01", "2024-01-02", "2024-01-03"]
            ).normalize(),
            "close": [10.0, 11.0, 12.0],
            "open": [10.0, 11.0, 12.0],
            "high": [10.0, 11.0, 12.0],
            "low": [10.0, 11.0, 12.0],
            "volume": [100, 120, 130],
            "rsi_2": [40.0, 60.0, 70.0],
        }
    )
    df = compute_indicators(raw)
    filters = pd.DataFrame({"FilterCode": ["T1"], "PythonQuery": ["(RSI_2 > 50)"]})
    sigs = run_screener(df, filters, "2024-01-02")
    out = run_1g_returns(df, sigs)
    assert list(out.columns) == [
        "FilterCode",
        "Symbol",
        "Date",
        "EntryClose",
        "ExitClose",
        "Side",
        "ReturnPct",
        "Win",
        "Reason",
    ]
    assert out["Reason"].isna().all()
    assert out.loc[0, "ReturnPct"] == pytest.approx((12.0 / 11.0 - 1) * 100)
