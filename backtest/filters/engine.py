from __future__ import annotations

import logging
import re
from typing import Mapping

import numpy as np
import pandas as pd

from backtest.cross import cross_down as _cross_down
from backtest.cross import (
    cross_over,
)
from backtest.cross import cross_up as _cross_up
from backtest.filters.normalize_expr import normalize_expr
from backtest.naming.aliases import normalize_token

log = logging.getLogger("backtest")

_TOKEN_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")

# Flag to allow evaluation of potentially unsafe expressions.  Tests or callers
# may toggle this module level variable if dangerous expressions should be
# executed instead of raising an error.  Defaults to ``False`` for safety.
UNSAFE_EVAL = False

# Names that should never appear in a filter expression.  Presence of any of
# these indicates a potentially dangerous expression.
_UNSAFE_TOKENS = {
    "os",
    "sys",
    "subprocess",
    "eval",
    "exec",
    "open",
}


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
    unsafe: list[str] = []
    for tok in _TOKEN_RE.findall(expr):
        if tok in {"and", "or", "not"} or tok.lower() in {"true", "false"}:
            continue
        if tok not in locals_map:
            if tok.startswith("_") or tok in _UNSAFE_TOKENS or "import" in tok:
                unsafe.append(tok)
            else:
                undefined.append(tok)
    if unsafe and not UNSAFE_EVAL:
        bad = ", ".join(sorted(set(unsafe)))
        raise SyntaxError(f"UNSAFE_EXPR: {bad}")
    if undefined:
        unknown = ", ".join(sorted(set(undefined)))
        raise NameError(f"Bilinmeyen değişkenler: {unknown}")


def _canonicalise_tokens(expr: str) -> str:
    expr = re.sub(r"(?<=\w)-(\s)*(?=\w)", "_", expr)
    expr = re.sub(r"([A-Za-z_][A-Za-z0-9_]*)\s+(\d+)", r"\1_\2", expr)

    def repl(m: re.Match[str]) -> str:
        return normalize_token(m.group(0))

    return _TOKEN_RE.sub(repl, expr)


_BOOL_RE = re.compile(r"\b(true|false)\b", flags=re.I)


def _normalise_boolean_literals(expr: str) -> str:
    """Replace case-insensitive boolean tokens with Python bool literals."""

    def repl(m: re.Match[str]) -> str:
        return m.group(1).capitalize()

    return _BOOL_RE.sub(repl, expr)


def evaluate(df: pd.DataFrame, expr: str) -> pd.Series:
    """Evaluate a normalised filter expression on *df*."""

    expr = normalize_expr(expr)[0]
    expr = _canonicalise_tokens(expr)
    expr = _normalise_boolean_literals(expr)
    locals_map = _build_locals(df)
    _validate_tokens(expr, locals_map)
    try:
        result = pd.eval(expr, engine="python", local_dict=locals_map)
        if isinstance(result, (bool, np.bool_, int, float)):
            return pd.Series([bool(result)] * len(df), index=df.index)
        return result
    except SyntaxError as e:
        # Propagate syntax errors so callers can decide how to handle them.
        raise SyntaxError(str(e)) from e
    except Exception as e:  # pragma: no cover - defensive
        log.exception("evaluate failed", extra={"extra_fields": {"expr": expr}})
        raise ValueError(f"evaluate failed: {expr} → {e}") from e


__all__ = ["evaluate", "cross_up", "cross_down"]
