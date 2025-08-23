from hypothesis import given, strategies as st
from backtest.portfolio.engine import PortfolioParams, size_risk_per_trade


@given(
    price=st.floats(min_value=1, max_value=1000),
    atr=st.floats(min_value=0.01, max_value=50),
)
def test_no_infinite_qty(price, atr):
    p = PortfolioParams()
    q = size_risk_per_trade(  # noqa: E501
        price=price, equity=1_000_000, params=p, atr_val=atr
    )
    assert q >= 0
