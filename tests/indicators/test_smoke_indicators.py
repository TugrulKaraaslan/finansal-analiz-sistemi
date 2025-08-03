import pandas as pd
import numpy as np
import types

import finansal_analiz_sistemi.indicators.provider as provider


def _simple_series():
    return pd.Series(np.linspace(1, 50, 50), index=pd.date_range("2024-01-01", periods=50))


def test_rsi_macd_ichimoku_smoke(monkeypatch):
    close = _simple_series()
    high = close + 1
    low = close - 1

    monkeypatch.setattr(provider, "backend", "local")

    rsi = provider.rsi(close)
    assert isinstance(rsi, pd.Series)
    assert len(rsi) == len(close)

    macd_df = provider.macd(close)
    assert isinstance(macd_df, pd.DataFrame)
    assert len(macd_df) == len(close)

    ich_df, span_df = provider.ichimoku(high, low, close)
    assert "ITS_9" in ich_df.columns
    assert not ich_df.empty
    assert not span_df.empty
