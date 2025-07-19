"""Unit tests for query_columns."""

import pandas as pd

import filter_engine


def test_extract_ignore_string_literals():
    """String literals should be ignored when extracting column names."""
    cols = filter_engine._extract_query_columns('aciklama == "BETA" and close > 0')
    assert cols == {"aciklama", "close"}


def test_apply_single_filter_string_literal():
    """Applying a filter with a string literal should succeed."""
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


def test_extract_bracket_notation():
    """Bracket notation should yield the inner column name."""
    expr = "close > df['BBM_20_2.0']"
    cols = filter_engine._extract_query_columns(expr)
    assert cols == {"close", "BBM_20_2.0"}
