import pandas as pd

from backtest.portfolio.costs import CostParams, apply_costs


def test_costs_non_negative():
    trades = pd.DataFrame(
        {
            "fill_price": [100, 101],
            "quantity": [10, 10],
            "side": ["BUY", "SELL"],
        }
    )
    out = apply_costs(trades, CostParams())
    cols = ["cost_commission", "cost_slippage", "cost_taxes", "cost_total"]
    assert (out[cols] >= 0).all().all()
