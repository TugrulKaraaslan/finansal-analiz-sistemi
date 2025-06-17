import pandas as pd
import pytest


@pytest.fixture
def sample_filtreler():
    return pd.DataFrame({
        "kod": ["F_OK", "F_MISS"],
        "PythonQuery": ["close > 10", "open > 5"],
    })


@pytest.fixture
def sample_indikator_df():
    return pd.DataFrame({
        "hisse_kodu": ["AAA"],
        "tarih": [pd.Timestamp("2025-01-01")],
        "close": [12],
    })
