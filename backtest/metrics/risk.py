"""Basic risk metrics.

This module provides small helpers to compute common risk statistics used in
backtests. All functions return ``float`` values and accept ``pandas`` inputs.
"""

from __future__ import annotations

import math

import pandas as pd


def sharpe_ratio(
    returns: pd.Series,
    rf: float = 0.0,
    freq: int = 252,
) -> float:
    """Return annualized Sharpe ratio.

    Parameters
    ----------
    returns: pd.Series
        Periodic returns expressed as decimals (e.g. 0.01 for 1%).
    rf: float, optional
        Risk‑free rate (annualized). Defaults to 0.0.
    freq: int, optional
        Number of periods per year. Defaults to 252 for daily data.
    """

    r = returns.astype(float)
    excess = r - (rf / freq)
    std = excess.std(ddof=0)
    if std == 0:
        return float("nan")
    return float(excess.mean() / std * math.sqrt(freq))


def sortino_ratio(
    returns: pd.Series,
    rf: float = 0.0,
    freq: int = 252,
) -> float:
    """Return annualized Sortino ratio using downside deviation."""

    r = returns.astype(float)
    excess = r - (rf / freq)
    downside = excess[excess < 0]
    dd = downside.std(ddof=0)
    if dd == 0:
        return float("nan")
    return float(excess.mean() / dd * math.sqrt(freq))


def max_drawdown(equity: pd.Series) -> float:
    """Return maximum drawdown of an equity curve.

    The result is a negative float representing the worst peak‑to‑trough
    decline.
    """

    e = equity.astype(float)
    peak = e.cummax()
    dd = e / peak - 1.0
    return float(dd.min())


def turnover(weights: pd.DataFrame) -> float:
    """Return portfolio turnover.

    Turnover is defined as ``0.5 * sum(|w_t - w_{t-1}|)`` across all periods
    and assets.
    """

    w = weights.fillna(0.0).astype(float)
    diff = w.diff().abs().sum(axis=1).sum()
    return float(diff / 2.0)


__all__ = [
    "sharpe_ratio",
    "sortino_ratio",
    "max_drawdown",
    "turnover",
]
