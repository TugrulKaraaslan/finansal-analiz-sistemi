"""Minimal conftest to avoid heavy dependencies."""

import glob
import os
import tempfile

import pandas as pd
import pytest


@pytest.fixture(autouse=True, scope="session")
def _cleanup_stale_locks():
    """Remove leftover ``.lock`` files from the temp directory."""
    for fp in glob.glob(os.path.join(tempfile.gettempdir(), "*.lock")):
        try:
            os.remove(fp)
        except OSError:
            pass
    yield


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


@pytest.fixture
def summary_df():
    """Minimal summary DataFrame for report tests."""
    return pd.DataFrame({"filtre_kodu": ["AAA"], "hisse_kodu": ["AAA"]})
