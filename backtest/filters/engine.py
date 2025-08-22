from __future__ import annotations
import pandas as pd
from backtest.cross import cross_up, cross_down


def evaluate(df: pd.DataFrame, expr: str) -> pd.Series:
    """Evaluate a boolean filter expression on ``df``.

    Rather than relying on ``DataFrame.eval`` (which only allows a restricted
    set of functions), the expression is evaluated using Python's ``eval`` with
    a sandboxed environment containing Series objects from ``df`` and the
    vectorised ``cross_up``/``cross_down`` helpers. This keeps the computation
    fully vectorised without resorting to ``apply`` or explicit loops.
    """
    if "cross_up" in expr or "cross_down" in expr:
        env = {c: df[c] for c in df.columns}
        env.update({"cross_up": cross_up, "cross_down": cross_down})
        safe_expr = expr.replace(" and ", " & ").replace(" or ", " | ")
        try:
            return eval(safe_expr, {"__builtins__": {}}, env)
        except Exception as e:
            raise ValueError(f"filter evaluation failed: {e}") from e
    try:
        return df.eval(expr, engine="python")
    except Exception as e:
        raise ValueError(f"filter evaluation failed: {e}") from e


__all__ = ["evaluate"]
