"""Test module for test_indicator_calc_hyp."""

import pandas as pd
import pytest

try:  # allow older pytest versions
    pytest.importorskip("hypothesis", allow_module_level=True)
except TypeError:  # pragma: no cover - fallback for pytest<7.2
    pytest.importorskip("hypothesis")
from hypothesis import given  # noqa: E402
from hypothesis import strategies as st  # noqa: E402

ta = pytest.importorskip("pandas_ta")
if not hasattr(ta, "psar"):
    pytest.skip("psar not available", allow_module_level=True)

import indicator_calculator as ic  # noqa: E402


@given(st.lists(st.floats(-1e6, 1e6), min_size=10, max_size=200))
def test_safe_ma_adds_column(xs):
    """Test test_safe_ma_adds_column."""
    df = pd.DataFrame({"close": xs})
    ic.safe_ma(df, 5, "sma")
    assert "sma_5" in df.columns
    assert len(df["sma_5"]) == len(xs)
    assert df["sma_5"].notna().all()
