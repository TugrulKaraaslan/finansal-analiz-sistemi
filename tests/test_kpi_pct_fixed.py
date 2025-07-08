"""Unit tests for kpi_pct_fixed."""

import pandas as pd

from report_stats import _normalize_pct


def test_pct_normalization():
    """Round fractional percentages to two decimal places."""
    assert _normalize_pct(pd.Series([0.128])).iat[0] == 0.13
