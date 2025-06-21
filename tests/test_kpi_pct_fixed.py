import pandas as pd
from report_stats import _normalize_pct


def test_pct_normalization():
    assert _normalize_pct(pd.Series([0.128])).iat[0] == 0.13
