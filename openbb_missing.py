"""
Fallback stubs for ``openbb.technical`` indicators.

These thin wrappers forward calls to the real OpenBB functions when
available and otherwise raise :class:`NotImplementedError`.
"""

from __future__ import annotations

from typing import Any, Callable

import pandas as pd
from cachetools import LRUCache

from utils.env_utils import positive_int_env

# Default size for the OpenBB function cache. The value can be overridden via
# the ``OPENBB_FUNC_CACHE_SIZE`` environment variable. Invalid or non-positive
# values fall back to this default of ``16``.
DEFAULT_CACHE_SIZE = 16
FUNC_CACHE_SIZE = positive_int_env("OPENBB_FUNC_CACHE_SIZE", DEFAULT_CACHE_SIZE)

__all__ = ["ichimoku", "macd", "rsi", "clear_cache", "is_available"]

try:  # pragma: no cover - optional dependency
    from openbb import obb  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    obb = None

# Cache for resolved OpenBB functions
# Limit size to avoid unbounded growth when called with many names
_FUNC_CACHE: LRUCache[str, Callable[..., Any]] = LRUCache(maxsize=FUNC_CACHE_SIZE)


def is_available() -> bool:
    """Return ``True`` when ``openbb.technical`` is available."""
    return getattr(obb, "technical", None) is not None


def clear_cache(size: int | None = None) -> None:
    """Empty the internal OpenBB function cache.

    Parameters
    ----------
    size : int, optional
        When provided and positive, the cache is recreated with the given
        ``maxsize`` instead of simply being cleared. This allows adjusting
        memory usage without reloading the module.
    """

    global _FUNC_CACHE
    if size is not None and size > 0:
        _FUNC_CACHE = LRUCache(maxsize=size)
    else:
        _FUNC_CACHE.clear()


def _call_openbb(func_name: str, **kwargs) -> object:
    """Call the requested helper under ``openbb.technical``.

    The matching OpenBB indicator is invoked when the :mod:`openbb`
    package is available. When either the dependency or the requested
    function is missing, :class:`NotImplementedError` is raised.

    Parameters
    ----------
    func_name : str
        Name of the technical indicator under ``obb.technical``.
    **kwargs
        Additional keyword arguments passed directly to the OpenBB
        function.

    Returns
    -------
    object
        Result produced by the OpenBB helper.

    Raises
    ------
    NotImplementedError
        If :mod:`openbb` or the requested function is unavailable.
    """
    if obb is None:
        raise NotImplementedError("OpenBB package is not installed")

    technical = getattr(obb, "technical", None)
    if technical is None:
        raise NotImplementedError("OpenBB technical module is unavailable")

    func = _FUNC_CACHE.get(func_name)
    if func is None:
        attr = getattr(technical, func_name, None)
        if not callable(attr):
            raise NotImplementedError(f"OpenBB indicator '{func_name}' is unavailable")
        _FUNC_CACHE[func_name] = attr
        func = attr

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
    """Return Ichimoku indicator frames produced via OpenBB.

    Parameters
    ----------
    high : pandas.Series
        High price series.
    low : pandas.Series
        Low price series.
    close : pandas.Series
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
    tuple[pandas.DataFrame, pandas.DataFrame]
        DataFrames containing classic Ichimoku and span columns.

    Raises
    ------
    NotImplementedError
        If :mod:`openbb` is not available.
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
    """Return MACD indicator columns computed via OpenBB.

    Parameters
    ----------
    close : pandas.Series
        Close price series.
    fast : int, optional
        Fast EMA period.
    slow : int, optional
        Slow EMA period.
    signal : int, optional
        Signal line period.

    Returns
    -------
    pandas.DataFrame
        DataFrame with MACD, signal and histogram columns.

    Raises
    ------
    NotImplementedError
        If :mod:`openbb` is not available.
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
    macd_cols = [c for c in res_df.columns if "macd" in c.lower()]
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
    close : pandas.Series
        Close price series.
    length : int, optional
        Lookback period.
    scalar : float, optional
        Multiplier used in calculation.
    drift : int, optional
        Difference period.

    Returns
    -------
    pandas.Series
        Relative strength index series.

    Raises
    ------
    NotImplementedError
        If :mod:`openbb` is not available.
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
    return res_df[col].rename(close.name or "rsi")
