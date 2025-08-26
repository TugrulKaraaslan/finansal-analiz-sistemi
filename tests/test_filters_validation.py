import sys

import pytest

from filters.module_loader import load_filters_from_module


def test_load_filters_from_module():
    df = load_filters_from_module("io_filters", ["*"])
    assert list(df.columns) == ["FilterCode", "PythonQuery"]
    assert not df.empty


def test_missing_columns_module(tmp_path):
    mod_path = tmp_path / "bad_filters.py"
    mod_path.write_text("FILTERS = [{\"FilterCode\": \"F1\"}]\n", encoding="utf-8")
    sys.path.insert(0, str(tmp_path))
    try:
        with pytest.raises(ValueError):
            load_filters_from_module("bad_filters")
    finally:
        sys.path.remove(str(tmp_path))


def test_missing_filters_attr(tmp_path):
    mod_path = tmp_path / "no_filters.py"
    mod_path.write_text("X = 1\n", encoding="utf-8")
    sys.path.insert(0, str(tmp_path))
    try:
        with pytest.raises(ValueError):
            load_filters_from_module("no_filters")
    finally:
        sys.path.remove(str(tmp_path))
