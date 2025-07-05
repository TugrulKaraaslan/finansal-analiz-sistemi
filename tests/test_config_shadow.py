import pytest


def _dummy(x=[]):  # noqa: B006 - test flake8-bugbear rule handling
    return x


def test_shadow_detection(monkeypatch, tmp_path):
    fake = tmp_path / "config.py"
    fake.write_text("x = 1")
    monkeypatch.syspath_prepend(str(tmp_path))
    with pytest.raises(RuntimeError, match="Shadow config.py detected"):
        import config_resolver  # noqa
