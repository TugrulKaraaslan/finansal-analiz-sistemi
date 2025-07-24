import importlib

from src.utils import excel_reader


def test_env_override_excel_cache_size(monkeypatch):
    monkeypatch.setenv("EXCEL_CACHE_SIZE", "5")
    mod = importlib.reload(excel_reader)
    assert mod._excel_cache.maxsize == 5
    monkeypatch.delenv("EXCEL_CACHE_SIZE", raising=False)
    importlib.reload(excel_reader)


def test_env_invalid_excel_cache_size(monkeypatch):
    monkeypatch.setenv("EXCEL_CACHE_SIZE", "0")
    mod = importlib.reload(excel_reader)
    assert mod._excel_cache.maxsize == 8
    monkeypatch.setenv("EXCEL_CACHE_SIZE", "-3")
    mod = importlib.reload(excel_reader)
    assert mod._excel_cache.maxsize == 8
    monkeypatch.delenv("EXCEL_CACHE_SIZE", raising=False)
    importlib.reload(excel_reader)


def test_clear_cache_resize(monkeypatch, tmp_path):
    """Cache should recreate itself when ``size`` is provided."""
    path = tmp_path / "c.xlsx"
    # build a dummy workbook
    import pandas as pd

    pd.DataFrame({"a": [1]}).to_excel(path, index=False)

    cache = excel_reader._WorkbookCache(maxsize=4)
    monkeypatch.setattr(excel_reader, "_excel_cache", cache)
    _ = excel_reader.open_excel_cached(path)
    assert len(excel_reader._excel_cache) == 1
    excel_reader.clear_cache(size=2)
    assert len(excel_reader._excel_cache) == 0
    assert excel_reader._excel_cache.maxsize == 2
