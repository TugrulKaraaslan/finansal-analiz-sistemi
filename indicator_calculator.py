from __future__ import annotations

import warnings

import pandas as pd

_PANDAS_TA_ERR: Exception | None = None
try:  # library is optional
    import pandas_ta as ta  # type: ignore
except Exception as err:  # pragma: no cover - executed when pandas_ta missing
    ta = None  # type: ignore
    warnings.warn(
        "pandas_ta module not found; ADX indicator will be unavailable",
        ImportWarning,
    )
    _PANDAS_TA_ERR = err


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
    if ta is None:  # pragma: no cover - depends on optional dependency
        raise NotImplementedError(
            "pandas_ta is required for adx_14; install pandas_ta to use this indicator"
        ) from _PANDAS_TA_ERR
    out = ta.adx(high, low, close, length=14)
    if out is None or "ADX_14" not in out:
        return pd.Series([float("nan")] * len(close), index=close.index)
    return out["ADX_14"]
