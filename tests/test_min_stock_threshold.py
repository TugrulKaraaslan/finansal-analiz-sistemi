"""Unit tests for min_stock_threshold."""

import pandas as pd

import filter_engine


def test_filter_skipped_when_below_threshold(monkeypatch):
    """Filters below the minimum stock count should be skipped."""
    monkeypatch.setattr(filter_engine, "MIN_STOCKS_PER_FILTER", 2)
    df = pd.DataFrame(
        {
            "hisse_kodu": ["AAA"],
            "tarih": [pd.Timestamp("2025-03-01")],
            "close": [1],
        }
    )
    result, info = filter_engine._apply_single_filter(df, "T_skip", "close > 0")
    assert result.empty
    assert info["durum"] == "BOS"
