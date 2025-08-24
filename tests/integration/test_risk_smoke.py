import pandas as pd

from backtest.risk.guards import RiskEngine


def test_risk_smoke(tmp_path):
    cfg = {
        "enabled": True,
        "exposure": {"per_symbol_max_pct": 0.05},
        "report": {"output_dir": str(tmp_path), "write_json": True},
    }
    engine = RiskEngine(cfg)
    orders = pd.DataFrame({"fill_price": [100.0, 101.0], "quantity": [100, 200]})  # noqa: E501
    dec = engine.decide(  # noqa: E501
        {"equity": 1_000_000, "daily_trades": 2},
        orders,
        None,
        equity=1_000_000,
        symbol_exposure=0,
    )
    assert dec.final_action in ("allow", "modify", "block")
