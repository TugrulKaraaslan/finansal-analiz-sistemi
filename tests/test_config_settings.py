import sys

import pytest

from config import filters_config, settings


def test_settings_types():
    assert isinstance(settings.START_DATE, str)
    assert isinstance(settings.CAPITAL, int)


def test_filter_list_type():
    assert isinstance(filters_config.FILTER_LIST, list)
    assert "FI" in filters_config.FILTER_LIST


def test_invalid_filter_module_raises(tmp_path):
    mod_path = tmp_path / "bad_filters.py"
    mod_path.write_text("FILTERS = [{\"FilterCode\": \"F1\"}]\n", encoding="utf-8")
    sys.path.insert(0, str(tmp_path))
    try:
        with pytest.raises(ValueError):
            filters_config._load_filter_codes({"filters": {"module": "bad_filters"}})
    finally:
        sys.path.remove(str(tmp_path))
