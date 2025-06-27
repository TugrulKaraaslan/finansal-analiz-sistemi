"""Minimal conftest to avoid heavy dependencies."""

import pandas as pd
import pytest


@pytest.fixture
def sample_filtreler():
    """Minimal filter definition for health-check tests."""
    return pd.DataFrame(
        {"FilterCode": ["F1"], "PythonQuery": ["ichimoku_conversionline > 0"]}
    )


@pytest.fixture
def sample_indikator_df():
    """Tiny indicator DataFrame used by health-check tests."""
    return pd.DataFrame({"ichimoku_conversionline": [1.23]})

