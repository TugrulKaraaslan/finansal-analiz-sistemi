from __future__ import annotations

from typing import Dict

from .runner import Result


def objective_primary(result: Result) -> float:
    """Primary objective function.

    Currently the Sharpe ratio is used as the primary metric.
    """

    return float(result.metrics.get("sharpe", 0.0))


def objective_penalty(result: Result, constraints: Dict[str, float]) -> float:
    """Penalty for violating constraints.

    Each constraint is a soft limit. When a metric exceeds the limit the
    penalty is increased by the amount of violation. This simple scheme keeps
    the implementation lightweight while still allowing tests to verify the
    arithmetic.
    """

    penalty = 0.0
    m = result.metrics
    if "maxdd_pct" in constraints and m.get("maxdd", 0) > constraints["maxdd_pct"]:
        penalty += m["maxdd"] - constraints["maxdd_pct"]
    if "max_turnover_pct" in constraints and m.get("turnover", 0) > constraints["max_turnover_pct"]:
        penalty += (m["turnover"] - constraints["max_turnover_pct"]) / 100.0
    if "max_trades" in constraints and m.get("trades", 0) > constraints["max_trades"]:
        penalty += (m["trades"] - constraints["max_trades"]) / 100.0
    return float(penalty)


def score(result: Result, constraints: Dict[str, float]) -> float:
    """Combined score = primary - penalty."""

    return objective_primary(result) - objective_penalty(result, constraints)
