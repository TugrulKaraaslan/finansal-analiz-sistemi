from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Any
import numpy as np
import pandas as pd

from .registry import StrategySpec


@dataclass
class Result:
    metrics: Dict[str, float]


def _compute_metrics(returns: pd.Series, spec: StrategySpec) -> Dict[str, float]:
    if returns.empty:
        return {
            "sharpe": 0.0,
            "sortino": 0.0,
            "cagr": 0.0,
            "maxdd": 0.0,
            "turnover": 0.0,
            "hit_rate": 0.0,
            "trades": 0,
        }
    mean = returns.mean()
    std = returns.std() or 1.0
    sharpe = mean / std * np.sqrt(252)
    downside = returns[returns < 0]
    sortino = mean / (downside.std() or 1.0) * np.sqrt(252)
    equity = (1 + returns).cumprod()
    peak = equity.cummax()
    dd = (peak - equity) / peak
    maxdd = dd.max() * 100
    turnover = len(returns) * float(spec.params.get("risk_per_trade_bps", 1))
    hit_rate = float((returns > 0).mean())
    trades = int(len(returns))
    years = len(returns) / 252 if len(returns) else 0
    cagr = (equity.iloc[-1] ** (1 / years) - 1) * 100 if years else 0.0
    return {
        "sharpe": float(sharpe),
        "sortino": float(sortino),
        "cagr": float(cagr),
        "maxdd": float(maxdd),
        "turnover": float(turnover),
        "hit_rate": float(hit_rate),
        "trades": trades,
    }


def run_strategy(spec: StrategySpec, data: pd.DataFrame, exec_cfg: Dict[str, Any] | None = None) -> Result:
    """Run a simple backtest strategy on provided returns data.

    Parameters
    ----------
    spec:
        Strategy specification describing filters and parameters. The current
        implementation ignores filters and only uses parameters for turnover
        calculation.
    data:
        DataFrame expected to have a ``returns`` column representing daily
        percentage returns (in decimal form). Only this column is used for
        computing metrics.
    exec_cfg:
        Placeholder for execution configuration; currently unused.
    """

    returns = data.get("returns")
    if returns is None:
        returns = pd.Series(dtype=float)
    metrics = _compute_metrics(pd.Series(returns), spec)
    return Result(metrics=metrics)
