from __future__ import annotations

"""Central filter compiler API.

This module exposes two helpers, :func:`compile_expression` and
:func:`compile_filters`, which transform the DSL used in filters into
callables that operate on a :class:`pandas.DataFrame` and return a boolean
``Series`` mask.

All normalisation rules from ``backtest.filters.normalize_expr`` are applied
by default and indicator/column aliases are resolved through
``backtest.naming.aliases.normalize_token``.  The resulting callables evaluate
expressions through ``backtest.filters.engine.evaluate``.
"""

from typing import Callable, List
import re

import pandas as pd

from backtest.filters.engine import evaluate
from backtest.filters.normalize_expr import normalize_expr
from backtest.naming.aliases import normalize_token

_TOKEN_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")


def _canonicalise(expr: str) -> str:
    """Replace indicator/column aliases with their canonical snake_case."""

    expr = re.sub(r"(?<=\w)-(\s)*(?=\w)", "_", expr)
    expr = re.sub(r"([A-Za-z_][A-Za-z0-9_]*)\s+(\d+)", r"\1_\2", expr)

    def repl(match: re.Match[str]) -> str:
        return normalize_token(match.group(0))

    return _TOKEN_RE.sub(repl, expr)


def compile_expression(expr: str, *, normalize: bool = True) -> Callable[[pd.DataFrame], pd.Series]:
    """Compile a single filter expression.

    Parameters
    ----------
    expr:
        Filter DSL/Python-like expression string.
    normalize:
        When ``True`` (default) ``normalize_expr`` is applied before
        compilation.

    Returns
    -------
    Callable[[pd.DataFrame], pd.Series]
        A function that evaluates the expression on a dataframe and returns a
        boolean mask.

    Raises
    ------
    ValueError
        If *expr* is empty or only whitespace.
    """

    if expr is None or not str(expr).strip():
        raise ValueError("expression must be a non-empty string")

    expr_str = str(expr).strip()
    if normalize:
        expr_str = normalize_expr(expr_str)[0]
    expr_str = _canonicalise(expr_str)

    def _fn(df: pd.DataFrame) -> pd.Series:
        return evaluate(df, expr_str)

    return _fn


def compile_filters(exprs: List[str], *, normalize: bool = True) -> List[Callable[[pd.DataFrame], pd.Series]]:
    """Compile multiple expressions to callables.

    Parameters
    ----------
    exprs:
        List of expression strings. Order is preserved in the returned list.
    normalize:
        Apply normalisation rules before compilation.

    Returns
    -------
    list[Callable[[pd.DataFrame], pd.Series]]
        List of compiled callables corresponding to *exprs*.
    """

    return [compile_expression(e, normalize=normalize) for e in exprs]


__all__ = ["compile_expression", "compile_filters"]

