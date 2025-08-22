from __future__ import annotations

import io
import keyword
import tokenize
from typing import Iterable, Set

from .normalize_expr import normalize_expr


def collect_series(expr: str | Iterable[str]) -> Set[str]:
    """Collect series tokens referenced in *expr*.

    ``expr`` may be a single expression string or an iterable of expressions.
    The expression(s) are first normalised via :func:`normalize_expr` and then
    tokenised.  All ``NAME`` tokens that are not Python keywords are returned as
    a set of strings.
    """

    if isinstance(expr, str):
        exprs = [expr]
    else:
        exprs = list(expr)

    out: Set[str] = set()
    for e in exprs:
        norm = normalize_expr(e)
        for tok in tokenize.generate_tokens(io.StringIO(norm).readline):
            if tok.type == tokenize.NAME and tok.string not in keyword.kwlist:
                out.add(tok.string)
    return out


__all__ = ["collect_series"]
