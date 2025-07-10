"""Lightweight wrappers around optional OpenBB technical indicators.

Each helper calls into :mod:`openbb` when the library is installed and
otherwise raises :class:`NotImplementedError`.  This keeps the rest of the
codebase agnostic to whether OpenBB is available.
"""

from __future__ import annotations

import pandas as pd

try:  # pragma: no cover - optional dependency
    from openbb import obb  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    obb = None


def _call_openbb(func_name: str, **kwargs):
    """Execute a technical indicator under ``obb.technical`` and return the result.

    Parameters
    ----------
    func_name : str
        Name of the function under ``obb.technical``.
    **kwargs : Any
        Keyword arguments forwarded to the OpenBB call.

    Returns
    -------
    Any
        Value returned by the OpenBB function.

    Raises
    ------
    NotImplementedError
        If :mod:`openbb` or the requested function is missing.
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
    """Return Ichimoku indicator DataFrames using OpenBB.

    Parameters
    ----------
    high : pd.Series
        High price series.
    low : pd.Series
        Low price series.
    close : pd.Series
        Close price series.
    conversion : int, optional
        Conversion line period.
    base : int, optional
        Base line period.
    lagging : int, optional
        Lagging span period.
    offset : int, optional
        Displacement for span lines.
    lookahead : bool, optional
        Whether to shift leading spans forward.

    Returns
    -------
    tuple[pd.DataFrame, pd.DataFrame]
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
    """Return MACD indicator columns using OpenBB.

    Parameters
    ----------
    close : pd.Series
        Close price series.
    fast : int, optional
        Fast EMA period.
    slow : int, optional
        Slow EMA period.
    signal : int, optional
        Signal line period.

    Returns
    -------
    pd.DataFrame
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
    """Return the RSI series computed via OpenBB.

    Parameters
    ----------
    close : pd.Series
        Close price series.
    length : int, optional
        Lookback period.
    scalar : float, optional
        Multiplier used in calculation.
    drift : int, optional
        Difference period.

    Returns
    -------
    pd.Series
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
