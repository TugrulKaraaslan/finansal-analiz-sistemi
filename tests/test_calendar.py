from __future__ import annotations

import pandas as pd
from backtest.calendars import add_next_close

def test_next_close():
    df = pd.DataFrame({
        "symbol":["AAA","AAA","AAA"],
        "date":pd.to_datetime(["2024-01-05","2024-01-08","2024-01-09"]).date,
        "close":[10, 11, 11.5],
        "open":[0,0,0],
        "high":[0,0,0],
        "low":[0,0,0],
        "volume":[1,1,1]
    })
    out = add_next_close(df)
    assert out.loc[0,"next_close"] == 11
    assert pd.isna(out.loc[2,"next_close"])
