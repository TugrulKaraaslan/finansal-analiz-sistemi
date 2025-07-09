"""Unit tests for key_columns."""


def test_required_columns_present(summary_df):
    """Summary DataFrame must include key columns used in merges."""
    assert {"filtre_kodu", "hisse_kodu"} <= set(summary_df.columns)
