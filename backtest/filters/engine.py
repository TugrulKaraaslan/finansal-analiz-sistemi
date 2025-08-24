from __future__ import annotations

from typing import Mapping
import re
import warnings
import pandas as pd

from backtest.logging_conf import get_logger
log = get_logger("engine")

from backtest.cross import (
    cross_up as _cross_up,
    cross_down as _cross_down,
    cross_over,
)
from backtest.filters.normalize_expr import normalize_expr

# 1) Tek doğru isim standardı – kabul edilen legacy alias'lar
ALIAS: dict[str, str] = {
    # Ichimoku
    "its_9": "ichimoku_conversionline",
    "iks_26": "ichimoku_baseline",
    # MACD
    "macd_12_26_9": "macd_line",
    "macds_12_26_9": "macd_signal",
    # Bollinger – boşluk hataları
    "bbm_20 2": "bbm_20_2",
    "bbu_20 2": "bbu_20_2",
    "bbl_20 2": "bbl_20_2",
}

DEPRECATED = set(ALIAS.keys())


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


def _build_locals(df: pd.DataFrame) -> dict[str, pd.Series]:
    env = {c: df[c] for c in df.columns}
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
            "CROSSUP": cross_up,
            "CROSSDOWN": cross_down,
            "crossOver": cross_up,
            "crossUnder": cross_down,
            "crossup": cross_up,
            "crossdown": cross_down,
        }
    )
    return env


def _validate_tokens(expr: str, locals_map: Mapping[str, object]):
    undefined: list[str] = []
    scan_expr = expr
    for alias, canon in ALIAS.items():
        if " " in alias and alias in scan_expr:
            scan_expr = scan_expr.replace(alias, canon)
    for tok in re.findall(r"[A-Za-z_][A-Za-z0-9_]*", scan_expr):
        if tok in {"and", "or", "not"}:
            continue
        if tok not in locals_map and tok not in ALIAS.values():
            undefined.append(tok)
    if undefined:
        unknown = ", ".join(sorted(set(undefined)))
        raise NameError(f"Bilinmeyen değişkenler: {unknown}")


def evaluate(df: pd.DataFrame, expr: str) -> pd.Series:
    expr = normalize_expr(expr)[0]
    locals_map = _build_locals(df)
    for k, v in ALIAS.items():
        if k in (expr or ""):
            msg = f"legacy alias used: {k} -> {v}; evaluated with canonical"
            warnings.warn(msg)
    _validate_tokens(expr, locals_map)
    canon_expr = expr
    for a, c in ALIAS.items():
        canon_expr = canon_expr.replace(a, c)
    try:
        return pd.eval(canon_expr, engine="python", local_dict=locals_map)
    except Exception as e:  # pragma: no cover - defensive
        log.exception("evaluate failed", extra={"extra_fields": {"expr": expr}})
        raise ValueError(f"evaluate failed: {expr} → {e}") from e


__all__ = ["evaluate", "cross_up", "cross_down"]
