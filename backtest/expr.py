from __future__ import annotations

import warnings
from backtest.filters.engine import evaluate as _engine_evaluate

_warned = False


def evaluate(df, expression):
    """Deprecated wrapper for :func:`backtest.filters.engine.evaluate`.

    Emits :class:`DeprecationWarning` on first use and delegates the call to
    the new filter evaluation engine.
    """
    global _warned
    if not _warned:
        warnings.warn(
            "backtest.expr.evaluate is deprecated; use backtest.filters.engine.evaluate",
            DeprecationWarning,
            stacklevel=2,
        )
        _warned = True
    return _engine_evaluate(df, expression)


__all__ = ["evaluate"]
