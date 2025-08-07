from pathlib import Path

import pytest
from config import filters_config, paths_config, settings


def test_settings_types():
    assert isinstance(settings.START_DATE, str)
    assert isinstance(settings.CAPITAL, int)


def test_paths_are_paths():
    assert isinstance(paths_config.DATA_PATH, Path)
    assert isinstance(paths_config.OUTPUT_PATH, Path)
    assert isinstance(paths_config.LOG_DIR, Path)


def test_filter_list_type():
    assert isinstance(filters_config.FILTER_LIST, list)


def test_invalid_filter_list_raises(monkeypatch, tmp_path):
    bad_csv = tmp_path / "bad.csv"
    bad_csv.write_text("Wrong;\n1;\n", encoding="utf-8")
    monkeypatch.setattr(filters_config, "_FILTERS_CSV", bad_csv)
    with pytest.raises(ValueError):
        filters_config._load_filter_codes()


def test_filter_list_missing_column_raises(monkeypatch, tmp_path):
    missing_csv = tmp_path / "missing.csv"
    missing_csv.write_text("Other\n1\n", encoding="utf-8")
    monkeypatch.setattr(filters_config, "_FILTERS_CSV", missing_csv)
    with pytest.raises(ValueError):
        filters_config._load_filter_codes()
