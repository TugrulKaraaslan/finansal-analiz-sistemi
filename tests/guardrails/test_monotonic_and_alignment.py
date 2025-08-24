import pandas as pd
import pytest

from backtest.guardrails.no_lookahead import assert_monotonic_index, verify_alignment


def test_assert_monotonic_index_fails_on_non_monotonic():
    df = pd.DataFrame({"a": [1, 2]}, index=[pd.Timestamp("2020-01-02"), pd.Timestamp("2020-01-01")])
    with pytest.raises(AssertionError):
        assert_monotonic_index(df)


def test_verify_alignment_length_mismatch():
    df1 = pd.DataFrame({"a": [1, 2, 3]}, index=pd.date_range("2020", periods=3))
    df2 = pd.DataFrame({"a": [1, 2]}, index=pd.date_range("2020", periods=2))
    with pytest.raises(AssertionError):
        verify_alignment({"f": df1, "s": df2})
