from backtest.strategy.objectives import objective_penalty, score
from backtest.strategy.runner import Result


def test_penalty_and_score():
    res = Result(metrics={"sharpe": 1.5, "maxdd": 30, "turnover": 700, "trades": 1500})
    constraints = {"maxdd_pct": 25, "max_turnover_pct": 600, "max_trades": 1200}
    pen = objective_penalty(res, constraints)
    assert pen > 0
    assert score(res, constraints) == res.metrics["sharpe"] - pen
