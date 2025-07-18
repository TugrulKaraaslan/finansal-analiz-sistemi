import openbb_missing as om


def test_public_exports():
    assert sorted(om.__all__) == ["ichimoku", "macd", "rsi"]


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
