import pandas as pd

from backtest.risk.guards import RiskEngine


def test_kill_switch_blocks(monkeypatch):
    monkeypatch.setenv("KILL_SWITCH", "1")
    engine = RiskEngine({"enabled": True})
    orders = pd.DataFrame({"fill_price": [100], "quantity": [1]})
    dec = engine.decide({}, orders, None, equity=1000, symbol_exposure=0)
    assert dec.final_action == "block"
