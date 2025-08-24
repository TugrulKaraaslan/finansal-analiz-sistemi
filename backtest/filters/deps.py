from __future__ import annotations

import io
import keyword
import tokenize
from typing import Iterable, List, Set, Tuple

from .normalize_expr import normalize_expr


def collect_series(expr: str | Iterable[str]) -> Set[str]:
    """Collect series tokens referenced in *expr*."""

    if isinstance(expr, str):
        exprs = [expr]
    else:
        exprs = list(expr)

    out: Set[str] = set()
    for e in exprs:
        norm, _ = normalize_expr(e)
        for tok in tokenize.generate_tokens(io.StringIO(norm).readline):
            if tok.type == tokenize.NAME:
                name = tok.string
                if name in keyword.kwlist or name in {"cross_up", "cross_down"}:
                    continue
                out.add(name)
    return out


def collect_macros(expr: str | Iterable[str]) -> List[Tuple[str, str, str]]:
    """Collect cross_up/cross_down macro calls from *expr*."""

    if isinstance(expr, str):
        exprs = [expr]
    else:
        exprs = list(expr)

    macros: List[Tuple[str, str, str]] = []
    for e in exprs:
        _, m = normalize_expr(e)
        macros.extend(m)
    return macros


__all__ = ["collect_series", "collect_macros"]
