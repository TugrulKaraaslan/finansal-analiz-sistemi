from __future__ import annotations

import pandas as pd
from backtest.backtester import run_1g_returns

def test_backtester_basic():
    df = pd.DataFrame({
        "symbol":["AAA","AAA"],
        "date":pd.to_datetime(["2024-01-05","2024-01-08"]).date,
        "close":[10.0, 11.0],
        "next_close":[11.0, None],
        "next_date":pd.to_datetime(["2024-01-08","2024-01-09"]).date,
    })
    sigs = pd.DataFrame({"FilterCode":["T1"],"Symbol":["AAA"],"Date":[pd.to_datetime("2024-01-05").date()]})
    out = run_1g_returns(df, sigs)
    assert round(out.loc[0,"ReturnPct"],2) == 10.0
