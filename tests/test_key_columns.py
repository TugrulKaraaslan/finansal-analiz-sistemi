"""Unit tests for key_columns."""

import pandas as pd
import pytest

from report_stats import _normalize_pct


@pytest.fixture
def summary_df():
    """Test summary_df."""
    return pd.DataFrame({"filtre_kodu": ["X"], "hisse_kodu": ["AAA"]})


def test_required_columns_present(summary_df):
    """Test test_required_columns_present."""
    assert {"filtre_kodu", "hisse_kodu"} <= set(summary_df.columns)


def test_normalize_pct():
    """Test test_normalize_pct."""
    ser = pd.Series([5.0, 0.07, -350])
    out = _normalize_pct(ser)
    assert out.tolist() == [0.05, 0.07, -3.5]
