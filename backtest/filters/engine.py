from __future__ import annotations

import re

import pandas as pd

from backtest.cross import cross_up, cross_down
from backtest.filters.normalize_expr import normalize_expr
from backtest.pipeline.precompute import precompute_needed


def evaluate(df: pd.DataFrame, expr: str) -> pd.Series:
    """Evaluate a boolean filter expression on ``df``.

    Rather than relying on ``DataFrame.eval`` (which only allows a restricted
    set of functions), the expression is evaluated using Python's ``eval`` with
    a sandboxed environment containing Series objects from ``df`` and the
    vectorised ``cross_up``/``cross_down`` helpers. This keeps the computation
    fully vectorised without resorting to ``apply`` or explicit loops.
    """
    norm = normalize_expr(expr)
    df = precompute_needed(df, [expr])
    if re.search(r"cross_?(?:up|down)", norm, re.I):
        env = {c: df[c] for c in df.columns}
        env.update(
            {
                "cross_up": cross_up,
                "cross_down": cross_down,
                "crossup": cross_up,
                "crossdown": cross_down,
            }
        )
        try:
            return eval(norm, {"__builtins__": {}}, env)
        except Exception as e:
            raise ValueError(f"filter evaluation failed: {e}") from e
    try:
        return df.eval(norm, engine="python")
    except Exception as e:
        raise ValueError(f"filter evaluation failed: {e}") from e


__all__ = ["evaluate"]
