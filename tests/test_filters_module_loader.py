import sys
import types

import pandas as pd
import pytest

from filters.module_loader import DEFAULT_FILTERS_MODULE, load_filters_from_module


def _make_module(name: str) -> types.ModuleType:
    mod = types.ModuleType(name)
    mod.FILTERS = [
        {"FilterCode": "F1", "PythonQuery": "close>0"},
        {"FilterCode": "F2", "PythonQuery": "volume>0"},
    ]
    return mod


def test_load_filters_from_module(monkeypatch):
    mod = _make_module("dummy_mod")
    monkeypatch.setitem(sys.modules, "dummy_mod", mod)
    df = load_filters_from_module("dummy_mod")
    assert list(df.columns) == ["FilterCode", "PythonQuery"]
    assert df.shape[0] == 2


def test_load_filters_include_pattern(monkeypatch):
    mod = _make_module("dummy_mod2")
    monkeypatch.setitem(sys.modules, "dummy_mod2", mod)
    df = load_filters_from_module("dummy_mod2", include=["F1"])
    assert df["FilterCode"].tolist() == ["F1"]


def test_load_filters_default_module(monkeypatch):
    mod = _make_module(DEFAULT_FILTERS_MODULE)
    monkeypatch.setitem(sys.modules, DEFAULT_FILTERS_MODULE, mod)
    df = load_filters_from_module(None)
    assert df["FilterCode"].tolist() == ["F1", "F2"]


def test_load_filters_missing(monkeypatch):
    bad_mod = types.ModuleType("bad_mod")
    monkeypatch.setitem(sys.modules, "bad_mod", bad_mod)
    with pytest.raises(ValueError):
        load_filters_from_module("bad_mod")
