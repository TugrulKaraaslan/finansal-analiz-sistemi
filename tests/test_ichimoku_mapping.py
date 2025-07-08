"""Test module for test_ichimoku_mapping."""

import importlib
import os
import sys

import pandas as pd

import utils
from finansal_analiz_sistemi import config as _cfg

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


importlib.reload(_cfg)  # test ortamında doğru yolu garantile
config = _cfg


def test_ichimoku_mapping_extends_raw_columns():
    """Test test_ichimoku_mapping_extends_raw_columns."""
    filters = pd.DataFrame(
        {"FilterCode": ["F1"], "PythonQuery": ["ichimoku_conversionline > 0"]}
    )
    utils.extract_columns_from_filters_cached.cache_clear()
    wanted = utils.extract_columns_from_filters_cached(
        filters.to_csv(index=False), tuple(), tuple()
    )
    assert "ichimoku_conversionline" in wanted
    extended = set(wanted)
    for raw, mapped in config.INDIKATOR_AD_ESLESTIRME.items():
        if mapped in wanted:
            extended.add(raw)
            extended.add(str(raw).upper())
    assert "its_9" in extended or "ITS_9" in extended
