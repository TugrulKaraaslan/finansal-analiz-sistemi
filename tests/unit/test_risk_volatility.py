import pandas as pd
from backtest.risk.guards import RiskEngine


def test_cb_volatility_prefers_specific_window_when_zero():
    cfg = {
        "circuit_breakers": {
            "volatility_halt": {
                "atr_window": 14,
                "atr_to_price_bps": 5000,
            }
        }
    }
    engine = RiskEngine(cfg)
    state = {}
    orders_df = pd.DataFrame()
    # atr_14 is zero which is a valid reading; atr fallback is large
    mkt_row = pd.Series({"close": 100, "atr_14": 0, "atr": 100})

    decision = engine.decide(
        state,
        orders_df,
        mkt_row,
        equity=0,
        symbol_exposure=0,
    )
    assert decision.final_action == "allow"
