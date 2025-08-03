"""Select technical indicator backend with graceful fallback."""
from __future__ import annotations

import logging
import os
from importlib import metadata as _metadata
from typing import Tuple

import pandas as pd

from openbb_missing import (
    ichimoku as _obb_ichimoku,
    macd as _obb_macd,
    rsi as _obb_rsi,
    is_available as _obb_available,
)

try:
    _metadata.version("pandas_ta")
    import pandas_ta as ta  # type: ignore
except Exception:  # pragma: no cover - optional dep missing
    ta = None  # type: ignore

logger = logging.getLogger(__name__)

__all__ = ["backend", "rsi", "macd", "ichimoku"]

BACKEND_ENV = "FAS_INDICATOR_BACKEND"

backend = None


def _detect_backend() -> str:
    env = os.getenv(BACKEND_ENV)
    if env:
        return env.lower()
    if _obb_available():
        return "openbb"
    if ta is not None:
        return "pandas_ta"
    return "local"


backend = _detect_backend()


def rsi(close: pd.Series, length: int = 14) -> pd.Series:
    if backend == "openbb":
        try:
            return _obb_rsi(close, length=length)
        except Exception as exc:  # pragma: no cover - runtime fallback
            logger.warning("OpenBB rsi failed: %s", exc)
    if backend in {"openbb", "pandas_ta"} and ta is not None:
        out = ta.rsi(close, length=length)
        if isinstance(out, pd.Series):
            return out.rename(close.name or f"rsi_{length}")
        return out.iloc[:, 0].rename(close.name or f"rsi_{length}")
    # local fallback
    delta = close.diff().fillna(0)
    up = delta.clip(lower=0)
    down = -delta.clip(upper=0)
    roll_up = up.ewm(span=length, adjust=False).mean()
    roll_down = down.ewm(span=length, adjust=False).mean()
    rs = roll_up / roll_down
    rsi_series = 100 - 100 / (1 + rs)
    return rsi_series.rename(close.name or f"rsi_{length}")


def macd(close: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> pd.DataFrame:
    if backend == "openbb":
        try:
            return _obb_macd(close, fast=fast, slow=slow, signal=signal)
        except Exception as exc:  # pragma: no cover
            logger.warning("OpenBB macd failed: %s", exc)
    if backend in {"openbb", "pandas_ta"} and ta is not None:
        df = ta.macd(close, fast=fast, slow=slow, signal=signal)
        cols = ["macd_line", "macd_hist", "macd_signal"]
        df.columns = cols[: len(df.columns)]
        return df
    # local fallback
    ema_fast = close.ewm(span=fast, adjust=False).mean()
    ema_slow = close.ewm(span=slow, adjust=False).mean()
    macd_line = ema_fast - ema_slow
    macd_signal = macd_line.ewm(span=signal, adjust=False).mean()
    return pd.DataFrame({"macd_line": macd_line, "macd_signal": macd_signal})


def ichimoku(
    high: pd.Series,
    low: pd.Series,
    close: pd.Series,
    conversion: int = 9,
    base: int = 26,
    lagging: int = 52,
    offset: int = 26,
    lookahead: bool = False,
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    if backend == "openbb":
        try:
            return _obb_ichimoku(
                high,
                low,
                close,
                conversion=conversion,
                base=base,
                lagging=lagging,
                offset=offset,
                lookahead=lookahead,
            )
        except Exception as exc:  # pragma: no cover
            logger.warning("OpenBB ichimoku failed: %s", exc)
    if backend in {"openbb", "pandas_ta"} and ta is not None and hasattr(ta, "ichimoku"):
        df = ta.ichimoku(high, low, close, conversion, base, lagging, offset)
        if isinstance(df, tuple):
            df = df[0]
        ich_df = df[["ITS_9", "IKS_26"]].copy()
        span_df = pd.DataFrame({
            "span_a": ((ich_df["ITS_9"] + ich_df["IKS_26"]) / 2).shift(offset),
            "span_b": ((high.rolling(lagging).max() + low.rolling(lagging).min()) / 2).shift(offset),
        })
        return ich_df, span_df
    # local fallback
    conv_high = high.rolling(conversion).max()
    conv_low = low.rolling(conversion).min()
    its = (conv_high + conv_low) / 2
    base_high = high.rolling(base).max()
    base_low = low.rolling(base).min()
    iks = (base_high + base_low) / 2
    span_a = ((its + iks) / 2).shift(offset)
    span_b = ((high.rolling(lagging).max() + low.rolling(lagging).min()) / 2).shift(offset)
    ich_df = pd.DataFrame({"ITS_9": its, "IKS_26": iks})
    span_df = pd.DataFrame({"span_a": span_a, "span_b": span_b})
    return ich_df, span_df
