"""
Fallback wrappers for optional OpenBB indicators.

Functions call into :mod:`openbb` when it is installed. If the package is
missing, the helpers raise a :class:`NotImplementedError` to signal the
missing dependency.
"""

from __future__ import annotations

import pandas as pd

try:  # pragma: no cover - optional dependency
    from openbb import obb  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    obb = None


def _call_openbb(func_name: str, **kwargs):
    """
    Return ``obb.technical.func_name`` result if available.

    Args:
        func_name: Name of the technical indicator function under ``obb``.
        **kwargs: Arguments forwarded to the OpenBB function.

    Returns:
        Result returned by the OpenBB helper.

    Raises:
        NotImplementedError: If :mod:`openbb` or the requested function is
            missing.
    """
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
    """
    Return Ichimoku indicator DataFrames generated via OpenBB.

    Args:
        high: High price series.
        low: Low price series.
        close: Close price series.
        conversion: Conversion line period.
        base: Base line period.
        lagging: Lagging span period.
        offset: Displacement for span lines.
        lookahead: Whether to shift leading spans forward.

    Returns:
        Two DataFrames containing classic Ichimoku and span columns.
    """
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


def macd(
    close: pd.Series,
    fast: int = 12,
    slow: int = 26,
    signal: int = 9,
) -> pd.DataFrame:
    """
    Return MACD indicator columns generated via OpenBB.

    Args:
        close: Close price series.
        fast: Fast EMA period.
        slow: Slow EMA period.
        signal: Signal line period.

    Returns:
        DataFrame with MACD, signal and histogram columns.
    """
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


def rsi(
    close: pd.Series,
    length: int = 14,
    scalar: float = 100.0,
    drift: int = 1,
) -> pd.Series:
    """
    Return the RSI series generated via OpenBB.

    Args:
        close: Close price series.
        length: Lookback period.
        scalar: Multiplier used in calculation.
        drift: Difference period.

    Returns:
        Relative strength index series.
    """
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
