"""Test module for test_query_columns."""

import pandas as pd

import filter_engine


def test_extract_ignore_string_literals():
    """Test test_extract_ignore_string_literals."""
    cols = filter_engine._extract_query_columns('aciklama == "BETA" and close > 0')
    assert cols == {"aciklama", "close"}


def test_apply_single_filter_string_literal():
    """Test test_apply_single_filter_string_literal."""
    df = pd.DataFrame(
        {
            "hisse_kodu": ["AAA"],
            "tarih": [pd.Timestamp("2025-03-01")],
            "close": [1],
            "aciklama": ["BETA"],
        }
    )
    _, info = filter_engine._apply_single_filter(df, "T1", 'aciklama == "BETA"')
    assert info["durum"] == "OK"
