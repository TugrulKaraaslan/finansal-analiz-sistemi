"""Unit tests for report."""

import pandas as pd


def test_no_dummy_filter_codes(summary_df):
    """Test test_no_dummy_filter_codes."""
    assert not summary_df["filtre_kodu"].str.contains("FiltreIndex_").any()
