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
