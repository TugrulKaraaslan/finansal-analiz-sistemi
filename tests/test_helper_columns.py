"""Unit tests for helper_columns."""

import preprocessor


def test_auto_columns_generated(big_df):
    """Preprocessor should compute helper columns like ``volume_tl``."""
    slim = big_df.head(1000).copy()
    slim["psar_long"] = slim["high"]
    slim["psar_short"] = slim["low"]
    out = preprocessor.on_isle_hisse_verileri(slim)
    assert {"volume_tl", "psar"}.issubset(out.columns)
