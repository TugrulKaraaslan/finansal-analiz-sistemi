"""Lightweight wrappers for optional OpenBB technical indicators.

Each function forwards to :mod:`openbb` when the package is available
and otherwise raises ``NotImplementedError`` so the rest of the codebase
remains optional-dependency agnostic.
"""

from __future__ import annotations

import pandas as pd

try:  # pragma: no cover - optional dependency
    from openbb import obb  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    obb = None


def _call_openbb(func_name: str, **kwargs):
    """Invoke an OpenBB technical analysis function when installed.

    Parameters
    ----------
    func_name : str
        Name of the function under ``obb.technical``.
    **kwargs : Any
        Arguments forwarded to the underlying OpenBB call.

    Returns
    -------
    Any
        Result returned by the OpenBB function.

    Raises
    ------
    NotImplementedError
        If the :mod:`openbb` package or the requested function is missing.
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
    """Return Ichimoku indicator results via OpenBB."""
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
    """Return MACD indicator DataFrame from OpenBB."""
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
    """Return the RSI Series calculated by OpenBB."""
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
