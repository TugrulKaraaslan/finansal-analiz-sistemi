import pandas as pd

from backtest.portfolio.costs import CostParams, apply_costs


def test_apply_costs_fixed_bps():
    trades = pd.DataFrame(
        {
            "fill_price": [100.0, 102.0],
            "quantity": [10, 10],
            "side": ["BUY", "SELL"],
            "close": [100.0, 102.0],
            "atr_14": [1.0, 1.2],
        }
    )
    params = CostParams(
        enabled=True,
        commission_bps=10.0,
        default_spread_bps=4.0,
        bps_per_1x_atr=0.0,
    )
    out = apply_costs(trades, params)
    assert "cost_total" in out and out["cost_total"].sum() > 0


def test_apply_costs_atr_slippage():
    trades = pd.DataFrame(
        {
            "fill_price": [100.0],
            "quantity": [100],
            "side": ["BUY"],
            "close": [100.0],
            "atr_14": [2.0],
        }
    )
    params = CostParams(
        enabled=True,
        commission_bps=0.0,
        default_spread_bps=0.0,
        bps_per_1x_atr=10.0,
    )
    out = apply_costs(trades, params)
    assert out.loc[0, "cost_slippage"] > 0
