from __future__ import annotations

from typing import Mapping
import re
import pandas as pd

from backtest.logging_conf import get_logger
log = get_logger("engine")

from backtest.cross import (
    cross_up as _cross_up,
    cross_down as _cross_down,
    cross_over,
)
from backtest.filters.normalize_expr import normalize_expr
from backtest.naming.aliases import normalize_token

_TOKEN_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")


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
    env = {}
    for c in df.columns:
        env[normalize_token(c)] = df[c]
    env.update({"cross_up": cross_up, "cross_down": cross_down})
    return env


def _validate_tokens(expr: str, locals_map: Mapping[str, object]):
    undefined: list[str] = []
    for tok in _TOKEN_RE.findall(expr):
        if tok in {"and", "or", "not"}:
            continue
        if tok not in locals_map:
            undefined.append(tok)
    if undefined:
        unknown = ", ".join(sorted(set(undefined)))
        raise NameError(f"Bilinmeyen değişkenler: {unknown}")


def _canonicalise_tokens(expr: str) -> str:
    expr = re.sub(r"(?<=\w)-(\s)*(?=\w)", "_", expr)
    expr = re.sub(r"([A-Za-z_][A-Za-z0-9_]*)\s+(\d+)", r"\1_\2", expr)

    def repl(m: re.Match[str]) -> str:
        return normalize_token(m.group(0))

    return _TOKEN_RE.sub(repl, expr)


def evaluate(df: pd.DataFrame, expr: str) -> pd.Series:
    expr = normalize_expr(expr)[0]
    expr = _canonicalise_tokens(expr)
    locals_map = _build_locals(df)
    _validate_tokens(expr, locals_map)
    try:
        return pd.eval(expr, engine="python", local_dict=locals_map)
    except Exception as e:  # pragma: no cover - defensive
        log.exception("evaluate failed", extra={"extra_fields": {"expr": expr}})
        raise ValueError(f"evaluate failed: {expr} → {e}") from e


__all__ = ["evaluate", "cross_up", "cross_down"]
