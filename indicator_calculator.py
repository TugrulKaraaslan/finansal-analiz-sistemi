from __future__ import annotations

import pandas as pd
import pandas_ta as ta


def sma_5(close: pd.Series) -> pd.Series:
    """Simple moving average with window 5."""
    return close.rolling(window=5, min_periods=5).mean()


def ema_13(close: pd.Series) -> pd.Series:
    """Exponential moving average with span 13."""
    return close.ewm(span=13, adjust=False).mean()


def rsi_14(close: pd.Series) -> pd.Series:
    """Relative Strength Index with period 14.

    Uses the classic Wilder's RSI formula. For fewer than 14 observations the
    result is NaN, matching pandas_ta behaviour.
    """
    delta = close.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(window=14, min_periods=14).mean()
    avg_loss = loss.rolling(window=14, min_periods=14).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi


def adx_14(high: pd.Series, low: pd.Series, close: pd.Series) -> pd.Series:
    """Average Directional Index with period 14.

    Delegates to ``pandas_ta.adx`` and gracefully handles cases where the input
    length is shorter than the calculation period by returning a series of NaNs.
    """
    out = ta.adx(high, low, close, length=14)
    if out is None or "ADX_14" not in out:
        return pd.Series([float("nan")] * len(close), index=close.index)
    return out["ADX_14"]
