from __future__ import annotations

import io
import keyword
import os
import re
import tokenize
from typing import Iterable, Set

from .normalize_expr import normalize_expr


def collect_series(expr: str | Iterable[str]) -> Set[str]:
    """Collect series tokens referenced in *expr*.

    ``expr`` may be a single expression string or an iterable of expressions.
    The expression(s) are first normalised via :func:`normalize_expr` and then
    tokenised.  All ``NAME`` tokens that are not Python keywords are returned
    as a set of strings.
    """

    if isinstance(expr, str):
        exprs = [expr]
    else:
        exprs = list(expr)

    out: Set[str] = set()
    cross_funcs = {"crossup", "crossdown"}
    cross_re = re.compile(
        r"cross(?:up|down)\(([^,]+),([^\)]+)\)",
        re.I,
    )
    rewrite = os.getenv("CROSS_REWRITE") == "1"
    for e in exprs:
        norm = normalize_expr(e)
        for tok in tokenize.generate_tokens(io.StringIO(norm).readline):
            if tok.type == tokenize.NAME:
                name = tok.string
                if name in keyword.kwlist or name.lower() in cross_funcs:
                    continue
                out.add(name)
        if rewrite:
            # add lag dependencies for cross rewrite
            norm_orig = normalize_expr(e, rewrite_cross=False)
            for m in cross_re.finditer(norm_orig):
                a = m.group(1).strip()
                b = m.group(2).strip()
                out.add(f"lag1__{a}")
                out.add(f"lag1__{b}")
    return out


__all__ = ["collect_series"]
