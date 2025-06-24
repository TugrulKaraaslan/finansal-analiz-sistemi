import pandas as pd
import pytest

from report_stats import _normalize_pct


@pytest.fixture
def summary_df():
    return pd.DataFrame({"filtre_kodu": ["X"], "hisse_kodu": ["AAA"]})


def test_required_columns_present(summary_df):
    assert {"filtre_kodu", "hisse_kodu"} <= set(summary_df.columns)


def test_normalize_pct():
    ser = pd.Series([5.0, 0.07, -350])
    out = _normalize_pct(ser)
    assert out.tolist() == [0.05, 0.07, -3.5]
