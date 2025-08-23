from backtest.portfolio.engine import (
    PortfolioParams,
    size_risk_per_trade,
    size_fixed_fraction,
)


def test_risk_sizing_basic():
    p = PortfolioParams(
        initial_equity=1_000_000, risk_per_trade_bps=50, atr_mult=2
    )  # noqa: E501
    q = size_risk_per_trade(  # noqa: E501
        price=100, equity=1_000_000, params=p, atr_val=1.5
    )
    assert q > 0


def test_fixed_fraction_basic():
    p = PortfolioParams(fixed_fraction=0.1)
    q = size_fixed_fraction(price=100, equity=1_000_000, params=p)
    assert q == 1000
