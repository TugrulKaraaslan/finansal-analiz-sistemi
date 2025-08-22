from __future__ import annotations

import pandas as pd

from backtest.filters.normalize_expr import normalize_expr
from backtest.filters.deps import collect_series
from backtest.filters.functions import make_crossup, make_crossdown
from backtest.pipeline.precompute import precompute_needed


def evaluate(df: pd.DataFrame, expr: str) -> pd.Series:
    """Evaluate a boolean filter expression on ``df``.

    The expression may contain logical operators ``and``/``or`` and
    ``CROSSUP``/``CROSSDOWN`` macros. These macros are expanded into temporary
    columns prior to evaluation so that ``DataFrame.eval`` can be used without
    direct function calls.
    """

    norm, macros = normalize_expr(expr)
    series = collect_series(expr)
    df = precompute_needed(df, series)

    for kind, a, b in macros:
        name = f"__{kind}__{a}__{b}"
        if name not in df.columns:
            if kind == "crossup":
                df[name] = make_crossup(df[a], df[b])
            else:
                df[name] = make_crossdown(df[a], df[b])
        norm = norm.replace(f"{kind.upper()}({a},{b})", name)

    try:
        return df.eval(norm, engine="python")
    except Exception as e:
        raise ValueError(f"filter evaluation failed: {e}") from e


__all__ = ["evaluate"]
