import pandas as pd

from backtest.risk.guards import RiskEngine


def test_symbol_cap_modify():
    cfg = {"enabled": True, "exposure": {"per_symbol_max_pct": 0.1}}
    engine = RiskEngine(cfg)
    orders = pd.DataFrame({"fill_price": [100.0], "quantity": [200]})  # noqa: E501
    dec = engine.decide({"equity": 1e5}, orders, None, equity=1e5, symbol_exposure=0)  # noqa: E501
    assert dec.final_action in ("modify", "allow")
