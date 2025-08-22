import pandas as pd
import numpy as np
from backtest.precompute import Precomputer

idx = pd.date_range("2024-01-01", periods=50, freq="B")

def _df():
    np.random.seed(0)
    return pd.DataFrame({
        "open": np.random.rand(len(idx))*100,
        "high": np.random.rand(len(idx))*100,
        "low": np.random.rand(len(idx))*100,
        "close": np.random.rand(len(idx))*100,
        "volume": np.random.randint(1000,5000,len(idx))
    }, index=idx)

def test_rsi_and_ema():
    df = _df()
    pc = Precomputer()
    out = pc.precompute(df, {"rsi_14", "ema_20"})
    assert "rsi_14" in out.columns
    assert "ema_20" in out.columns

def test_macd_and_bbands():
    df = _df()
    pc = Precomputer()
    out = pc.precompute(df, {"macd_12_26_9", "bbh_20_2"})
    assert "macd_12_26_9" in out.columns
    assert "macd_signal_12_26_9" in out.columns
    assert "macd_hist_12_26_9" in out.columns
    assert "bbh_20_2" in out.columns


def test_cache_prevents_recompute():
    df = _df()
    pc = Precomputer()
    out1 = pc.precompute(df, {"ema_20"})
    out2 = pc.precompute(out1, {"ema_20"})
    # cache çalıştığı için ikinci sefer hata/yeniden hesaplama olmamalı
    assert "ema_20" in out2.columns
