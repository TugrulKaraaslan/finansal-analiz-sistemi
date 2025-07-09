"""Tests for the Excel report generation helpers."""


def test_no_dummy_filter_codes(summary_df):
    """Ensure the summary contains no placeholder filter codes."""
    assert not summary_df["filtre_kodu"].str.contains("FiltreIndex_").any()
