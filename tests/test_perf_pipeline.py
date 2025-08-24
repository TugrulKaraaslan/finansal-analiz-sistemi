from pathlib import Path

import pandas as pd

from backtest.indicators.precompute import (
    collect_required_indicators,
    precompute_for_chunk,
)
from backtest.io.panel_cache import build_panel_parquet, load_panel_parquet


def test_build_and_load_parquet(tmp_path: Path):
    df = pd.DataFrame({"date": ["2024-01-01"], "close": [100]})
    p = tmp_path / "panel.parquet"
    df.to_parquet(p, index=False)
    out = load_panel_parquet(p)
    assert "close" in out.columns


def test_precompute_chunk():
    df = pd.DataFrame({"close": [100, 101, 102, 103, 104]})
    out = precompute_for_chunk(df, {"sma", "ema", "rsi"})
    assert "sma_20" in out.columns
    assert "ema_20" in out.columns
    assert "rsi_14" in out.columns


def test_collect_indicators():
    df = pd.DataFrame({"PythonQuery": ["sma_20 > close", "rsi_14 < 30"]})
    out = collect_required_indicators(df)
    assert "sma" in out and "rsi" in out
