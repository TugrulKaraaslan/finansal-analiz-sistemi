"""Stubs for missing OpenBB functionality.

This module defines placeholder functions for pandas-ta features not yet
supported by OpenBB. Each function simply raises ``NotImplementedError``
to signal that an equivalent implementation is unavailable.
"""

from __future__ import annotations

import pandas as pd

try:  # pragma: no cover - optional dependency
    from openbb import obb  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    obb = None


def tema(*_args, **_kwargs):
    """Placeholder for :func:`pandas_ta.tema`."""
    raise NotImplementedError("openbb equivalent for 'tema' is missing")


def Strategy(*_args, **_kwargs):  # noqa: N802
    """Placeholder for :class:`pandas_ta.Strategy`."""
    raise NotImplementedError("openbb equivalent for 'Strategy' is missing")


def strategy(*_args, **_kwargs):
    """Placeholder for ``DataFrame.ta.strategy``."""
    raise NotImplementedError("openbb equivalent for 'strategy' is missing")


def psar(*_args, **_kwargs):
    """Placeholder for ``DataFrame.ta.psar`` or :func:`pandas_ta.psar`."""
    raise NotImplementedError("openbb equivalent for 'psar' is missing")


def _call_openbb(func_name: str, **kwargs):
    """Invoke an OpenBB technical analysis function if available."""
    if obb is None:
        raise NotImplementedError(f"openbb equivalent for '{func_name}' is missing")
    func = getattr(obb.technical, func_name, None)
    if func is None:
        raise NotImplementedError(f"openbb equivalent for '{func_name}' is missing")
    return func(**kwargs)


def ichimoku(
    high: pd.Series,
    low: pd.Series,
    close: pd.Series,
    conversion: int = 9,
    base: int = 26,
    lagging: int = 52,
    offset: int = 26,
    lookahead: bool = False,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Wrapper for OpenBB ``ichimoku`` returning pandas objects."""
    df = pd.DataFrame(
        {
            "date": close.index,
            "high": high.values,
            "low": low.values,
            "close": close.values,
        }
    )
    obb_obj = _call_openbb(
        "ichimoku",
        data=df.to_dict("records"),
        conversion=conversion,
        base=base,
        lagging=lagging,
        offset=offset,
        lookahead=lookahead,
    )
    res_df = pd.DataFrame(obb_obj.results).set_index("date")
    span_cols = [c for c in res_df.columns if c.startswith("span_")]
    ich_cols = [c for c in res_df.columns if c not in span_cols]
    return res_df[ich_cols], res_df[span_cols]


def rsi(
    close: pd.Series,
    length: int = 14,
    scalar: float = 100.0,
    drift: int = 1,
) -> pd.Series:
    """Wrapper for OpenBB ``rsi`` returning a Series."""
    df = pd.DataFrame({"date": close.index, "close": close.values})
    obb_obj = _call_openbb(
        "rsi",
        data=df.to_dict("records"),
        target="close",
        length=length,
        scalar=scalar,
        drift=drift,
    )
    res_df = pd.DataFrame(obb_obj.results).set_index("date")
    rsi_col = [c for c in res_df.columns if c.lower().startswith("close_rsi")]
    col = rsi_col[0] if rsi_col else res_df.columns[-1]
    return res_df[col].rename(close.name)


def macd(
    close: pd.Series,
    fast: int = 12,
    slow: int = 26,
    signal: int = 9,
) -> pd.DataFrame:
    """Wrapper for OpenBB ``macd`` returning a DataFrame."""
    df = pd.DataFrame({"date": close.index, "close": close.values})
    obb_obj = _call_openbb(
        "macd",
        data=df.to_dict("records"),
        target="close",
        fast=fast,
        slow=slow,
        signal=signal,
    )
    res_df = pd.DataFrame(obb_obj.results).set_index("date")
    macd_cols = [c for c in res_df.columns if c.lower().startswith("close_macd")]
    return res_df[macd_cols]


def stochrsi(*_args, **_kwargs):
    """Placeholder for :func:`pandas_ta.stochrsi`."""
    raise NotImplementedError("openbb equivalent for 'stochrsi' is missing")


MISSING_FUNCTIONS = [
    "tema",
    "Strategy",
    "strategy",
    "psar",
    "stochrsi",
]
