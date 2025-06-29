import pandas as pd
import pytest


@pytest.fixture
def summary_df():
    return pd.DataFrame({"filtre_kodu": ["T2_Tn"], "hisse_kodu": ["AAA"]})


def test_no_dummy_filter_codes(summary_df):
    assert not summary_df["filtre_kodu"].str.contains("FiltreIndex_").any()
