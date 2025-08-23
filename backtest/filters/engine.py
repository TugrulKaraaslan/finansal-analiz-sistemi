from __future__ import annotations

import re
import warnings

import pandas as pd
from backtest.cross import (
    cross_up as _cross_up,
    cross_down as _cross_down,
    cross_over,
    cross_under,
)

# Kontrollü legacy alias → canonical
ALIAS: dict[str, str] = {
    "its_9": "ichimoku_conversionline",
    "iks_26": "ichimoku_baseline",
    "macd_12_26_9": "macd_line",
    "macds_12_26_9": "macd_signal",
    "bbm_20 2": "bbm_20_2",
    "bbu_20 2": "bbu_20_2",
    "bbl_20 2": "bbl_20_2",
}


def _build_locals(df: pd.DataFrame) -> dict[str, pd.Series]:
    env: dict[str, pd.Series] = {c: df[c] for c in df.columns}
    for c in list(df.columns):
        lc = c.lower()
        if lc not in env:
            env[lc] = df[c]
    for k, v in ALIAS.items():
        if v in df.columns:
            env[k] = df[v]
    env.update(
        {
            "cross_up": cross_up,
            "cross_down": cross_down,
            "crossup": cross_up,
            "crossdown": cross_down,
            "CROSSUP": cross_up,
            "CROSSDOWN": cross_down,
        }
    )
    return env


def evaluate(df: pd.DataFrame, expr: str) -> pd.Series:
    locals_map = _build_locals(df)
    for k, v in ALIAS.items():
        if re.search(rf"\b{re.escape(k)}\b", expr):
            warnings.warn(f"legacy alias '{k}' detected; use '{v}'", stacklevel=2)
    try:
        return pd.eval(expr, engine="python", local_dict=locals_map)
    except Exception as e:
        raise ValueError(f"evaluate failed: {expr} → {e}") from e


def cross_up(a: pd.Series, b: pd.Series | float | int) -> pd.Series:
    if isinstance(b, pd.Series):
        out = _cross_up(a, b)
    else:
        out = cross_over(a, b)
    out.iloc[-1] = False
    return out.fillna(False)


def cross_down(a: pd.Series, b: pd.Series | float | int) -> pd.Series:
    if isinstance(b, pd.Series):
        if b.nunique() == 1:
            level = b.iloc[0]
            out = (a.shift(1) > level) & (a <= level)
        else:
            out = _cross_down(a, b)
    else:
        out = (a.shift(1) > b) & (a <= b)
    out.iloc[-1] = False
    return out.fillna(False)


__all__ = ["evaluate", "cross_up", "cross_down"]
