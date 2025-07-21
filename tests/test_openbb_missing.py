import pytest

import openbb_missing as om


def test_public_exports():
    expected = [
        "clear_cache",
        "ichimoku",
        "is_available",
        "macd",
        "rsi",
    ]
    assert sorted(om.__all__) == expected


def test_wrappers_exist():
    for name in om.__all__:
        assert hasattr(om, name)


def test_call_openbb_populates_cache(monkeypatch):
    """_call_openbb should cache resolved functions."""

    calls = []

    class DummyTech:
        def foo(self, x: int) -> int:
            calls.append(x)
            return x

    dummy = type("DummyOBB", (), {"technical": DummyTech()})()

    monkeypatch.setattr(om, "obb", dummy)
    monkeypatch.setattr(om, "_FUNC_CACHE", om.LRUCache(maxsize=4))

    out1 = om._call_openbb("foo", x=1)
    out2 = om._call_openbb("foo", x=2)

    assert out1 == 1 and out2 == 2
    assert calls == [1, 2]
    assert "foo" in om._FUNC_CACHE
    assert len(om._FUNC_CACHE) == 1


def test_call_openbb_package_missing(monkeypatch):
    """NotImplementedError should be raised when OpenBB is absent."""

    monkeypatch.setattr(om, "obb", None)
    monkeypatch.setattr(om, "_FUNC_CACHE", om.LRUCache(maxsize=4))

    with pytest.raises(NotImplementedError, match="package"):
        om._call_openbb("foo")


def test_call_openbb_function_missing(monkeypatch):
    """NotImplementedError should be raised for unknown functions."""

    class DummyTech:
        pass

    dummy = type("DummyOBB", (), {"technical": DummyTech()})()

    monkeypatch.setattr(om, "obb", dummy)
    monkeypatch.setattr(om, "_FUNC_CACHE", om.LRUCache(maxsize=4))

    with pytest.raises(NotImplementedError, match="bar"):
        om._call_openbb("bar")


def test_clear_cache(monkeypatch):
    """clear_cache should drop cached functions."""

    class DummyTech:
        def foo(self, x: int) -> int:
            return x

    dummy = type("DummyOBB", (), {"technical": DummyTech()})()

    monkeypatch.setattr(om, "obb", dummy)
    monkeypatch.setattr(om, "_FUNC_CACHE", om.LRUCache(maxsize=4))

    om._call_openbb("foo", x=1)
    assert len(om._FUNC_CACHE) == 1
    om.clear_cache()
    assert len(om._FUNC_CACHE) == 0


def test_is_available_reflects_import(monkeypatch):
    """is_available should detect the presence of the OpenBB package."""
    monkeypatch.setattr(om, "obb", object())
    assert om.is_available() is True
    monkeypatch.setattr(om, "obb", None)
    assert om.is_available() is False


def test_env_override_cache_size(monkeypatch):
    """Environment variable should configure cache size."""
    import importlib

    monkeypatch.setenv("OPENBB_FUNC_CACHE_SIZE", "7")
    mod = importlib.reload(om)
    assert mod._FUNC_CACHE.maxsize == 7
    monkeypatch.delenv("OPENBB_FUNC_CACHE_SIZE", raising=False)
    importlib.reload(om)


def test_env_invalid_cache_size(monkeypatch):
    """Invalid or non-positive values should revert to the default."""
    import importlib

    monkeypatch.setenv("OPENBB_FUNC_CACHE_SIZE", "0")
    mod = importlib.reload(om)
    assert mod._FUNC_CACHE.maxsize == 16
    monkeypatch.setenv("OPENBB_FUNC_CACHE_SIZE", "-5")
    mod = importlib.reload(om)
    assert mod._FUNC_CACHE.maxsize == 16
    monkeypatch.delenv("OPENBB_FUNC_CACHE_SIZE", raising=False)
    importlib.reload(om)
