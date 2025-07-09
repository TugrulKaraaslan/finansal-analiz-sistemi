"""Unit tests for key_columns."""
import pandas as pd
from report_stats import _normalize_pct

def test_required_columns_present(summary_df):
    """Summary DataFrame must include key columns used in merges."""
    assert {"filtre_kodu", "hisse_kodu"} <= set(summary_df.columns)


def test_normalize_pct():
    """Whole-number percentages should be scaled to fractional form."""
    ser = pd.Series([5.0, 0.07, -350])
    out = _normalize_pct(ser)
    assert out.tolist() == [0.05, 0.07, -3.5]
