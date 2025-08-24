import pandas as pd

from backtest.risk.guards import RiskEngine


def test_kill_switch_blocks(monkeypatch):
    cfg = {"enabled": True, "kill_switch_env": "KSW"}
    engine = RiskEngine(cfg)
    monkeypatch.setenv("KSW", "1")
    dec = engine.decide(
        {"equity": 1e6},
        orders_df=pd.DataFrame(),
        mkt_row=None,
        equity=1e6,
        symbol_exposure=0,
    )
    assert dec.final_action == "block"
