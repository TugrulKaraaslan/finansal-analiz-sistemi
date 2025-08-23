from hypothesis import given, strategies as st
import pytest

from backtest.guardrails.no_lookahead import detect_future_refs


@given(k=st.integers(min_value=1, max_value=10))
def test_leakage_penalty_detects_negative_shift(k):
    expr = f"close.shift(-{k})"
    with pytest.raises(AssertionError):
        detect_future_refs(expr)
