"""Unit tests for settings_path."""

import sys
from pathlib import Path


def test_env_override(monkeypatch):
    """Environment variable should override the default settings path."""
    monkeypatch.setenv("FAS_SETTINGS_FILE", "/tmp/custom.yaml")
    from finansal_analiz_sistemi.config import get_settings_path

    assert str(get_settings_path()) == str(Path("/tmp/custom.yaml").resolve())


def test_colab_path(monkeypatch):
    """Colab runtime must point to the drive-mounted settings file."""
    monkeypatch.delenv("FAS_SETTINGS_FILE", raising=False)
    monkeypatch.setitem(sys.modules, "google.colab", object())
    from finansal_analiz_sistemi.config import get_settings_path

    assert "/content/drive/MyDrive/finansal-analiz-sistemi" in str(get_settings_path())
    sys.modules.pop("google.colab", None)


def test_local_path(monkeypatch):
    """Local environment falls back to repository ``settings.yaml``."""
    monkeypatch.delenv("FAS_SETTINGS_FILE", raising=False)
    sys.modules.pop("google.colab", None)
    from finansal_analiz_sistemi.config import get_settings_path

    expected = Path(__file__).resolve().parents[1] / "settings.yaml"
    assert get_settings_path() == expected
