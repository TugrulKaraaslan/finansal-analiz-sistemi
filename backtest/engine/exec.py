"""Execution helpers with guardrails.

Currently only a very small subset of the intended functionality is
implemented: signals are shifted by one bar to ensure T+1 execution.
"""
from __future__ import annotations

import pandas as pd
from backtest.guardrails.no_lookahead import enforce_t_plus_one


def apply_t_plus_one(signals: pd.Series | pd.DataFrame, cfg: dict | None = None):
    """Return *signals* shifted by one period.

    The helper calls :func:`enforce_t_plus_one` to record the configuration
    and then shifts the signal series forward by one bar, ensuring that a
    signal generated on day *t* is executed on day *t+1*.
    """
    enforce_t_plus_one(cfg or {})
    return signals.shift(1)
