import pandas as pd
from hypothesis import given
from hypothesis import strategies as st

import indicator_calculator as ic


@given(st.lists(st.floats(-1e6, 1e6), min_size=10, max_size=200))
def test_safe_ma_adds_column(xs):
    df = pd.DataFrame({"close": xs})
    ic.safe_ma(df, 5, "sma")
    assert "sma_5" in df.columns
    assert len(df["sma_5"]) == len(xs)
    assert df["sma_5"].notna().all()
