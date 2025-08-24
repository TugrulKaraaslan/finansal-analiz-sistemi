import pandas as pd

from backtest.portfolio.engine import PortfolioParams
from backtest.portfolio.simulator import PortfolioSim


def test_simulator_smoke(tmp_path):
    p = PortfolioParams()
    sim = PortfolioSim(p)
    # 3 gün, 1 sembol mock
    dates = pd.date_range("2025-03-07", "2025-03-09", freq="D")
    sig = pd.DataFrame(
        {
            "date": dates,
            "symbol": "AAA",
            "entry_long": [1, 0, 0],
            "exit_long": [0, 1, 0],
        }
    )
    mkt = pd.DataFrame(
        {
            "date": dates,
            "symbol": "AAA",
            "close": [100, 101, 102],
            "high": [101, 102, 103],
            "low": [99, 100, 101],
        }
    )
    for d in dates:
        sd = sig[sig["date"] == d]
        md = mkt[mkt["date"] == d]
        sim.step(d.strftime("%Y-%m-%d"), sd, md)
    sim.finalize(tmp_path)
    assert (tmp_path / "daily_equity.csv").exists()
