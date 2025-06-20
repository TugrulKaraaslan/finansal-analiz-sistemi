import pandas as pd
import pytest

try:
    pd.set_option("future.no_silent_downcasting", True)
except (AttributeError, KeyError, pd.errors.OptionError):
    # Pandas <2.2'de bu seçenek yok; sessizce atla.
    pass


@pytest.fixture
def sample_filtreler():
    return pd.DataFrame(
        {
            "kod": ["T0", "T1"],
            "PythonQuery": ["close > 0", "volume > 0"],
        }
    )


@pytest.fixture
def sample_indikator_df():
    return pd.DataFrame({"close": [10, 11], "relative_volume": [1.2, 1.3]})
