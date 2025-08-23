import pandas as pd
import pytest

from backtest.metrics import (
    max_drawdown,
    sharpe_ratio,
    sortino_ratio,
    turnover,
)


def test_basic_risk_metrics():
    returns = pd.Series([0.05, -0.02, 0.03, -0.01])
    equity = (1 + returns).cumprod()
    weights = pd.DataFrame({"w": [1.0, 0.5, 1.0, 0.0]})

    assert sharpe_ratio(returns, freq=1) == pytest.approx(
        0.436852028,
        rel=1e-6,
    )
    assert sortino_ratio(returns, freq=1) == pytest.approx(
        2.5,
        rel=1e-6,
    )
    assert max_drawdown(equity) == pytest.approx(-0.02, rel=1e-6)
    assert turnover(weights) == pytest.approx(1.0, rel=1e-6)
