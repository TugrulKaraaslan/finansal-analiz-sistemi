from __future__ import annotations

import pandas as pd

from backtest.indicators import compute_indicators


def test_compute_indicators_defaults():
    df = pd.DataFrame(
        {
            "symbol": ["AAA"],
            "date": pd.to_datetime(["2024-01-01"]).date,
            "close": [10.0],
            "volume": [100],
        }
    )
    out = compute_indicators(df)
    assert "rsi_14" in out.columns
