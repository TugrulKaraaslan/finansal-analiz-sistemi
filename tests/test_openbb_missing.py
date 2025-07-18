import openbb_missing as om


def test_public_exports():
    assert sorted(om.__all__) == ["ichimoku", "macd", "rsi"]


def test_wrappers_exist():
    for name in om.__all__:
        assert hasattr(om, name)
