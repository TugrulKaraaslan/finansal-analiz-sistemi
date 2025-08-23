import pandas as pd
from hypothesis import given, strategies as st
from backtest.risk.guards import RiskEngine


@given(
    price=st.floats(min_value=1, max_value=1000),
    qty=st.integers(min_value=1, max_value=1000),
)
def test_never_exceeds_per_symbol_cap(price, qty):
    cfg = {"enabled": True, "exposure": {"per_symbol_max_pct": 0.2}}
    engine = RiskEngine(cfg)  # noqa: E501
    orders = pd.DataFrame({"fill_price": [price], "quantity": [qty]})  # noqa: E501
    dec = engine.decide(
        {"equity": 1e6}, orders, None, equity=1e6, symbol_exposure=0
    )  # noqa: E501
    if dec.final_action == "modify":
        cap_cash = 1e6 * 0.2
        new = [r for r in dec.reasons if r.reason == "per_symbol_cap"][
            -1
        ].details[  # noqa: E501
            "new"
        ]
        assert abs(new) <= cap_cash + 1e-6
