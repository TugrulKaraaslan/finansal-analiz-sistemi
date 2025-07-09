"""Unit tests for settings_fallback."""

import importlib

import settings


def test_invalid_depth_fallback(tmp_path, monkeypatch):
    """Invalid integer values fall back to the default depth."""
    cfg = tmp_path / "settings.yaml"
    cfg.write_text("max_filter_depth: bad\n")
    monkeypatch.setenv("FAS_SETTINGS_FILE", str(cfg))
    importlib.reload(settings)
    assert settings.MAX_FILTER_DEPTH == 7
    monkeypatch.delenv("FAS_SETTINGS_FILE", raising=False)
    importlib.reload(settings)
    assert settings.MAX_FILTER_DEPTH == 7


def test_invalid_yaml_fallback(tmp_path, monkeypatch):
    """Malformed YAML should not override configuration defaults."""
    cfg = tmp_path / "settings.yaml"
    cfg.write_text("invalid: [\n")
    monkeypatch.setenv("FAS_SETTINGS_FILE", str(cfg))
    importlib.reload(settings)
    assert settings.MAX_FILTER_DEPTH == 7
    monkeypatch.delenv("FAS_SETTINGS_FILE", raising=False)
    importlib.reload(settings)
