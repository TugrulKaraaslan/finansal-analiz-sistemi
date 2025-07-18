"""Unit tests for config_defaults."""

import importlib

from finansal_analiz_sistemi import config

CONSTANTS = [
    "ALIM_ZAMANI",
    "TR_HOLIDAYS_REMOVE",
    "OHLCV_MAP",
    "INDIKATOR_AD_ESLESTIRME",
    "SERIES_SERIES_CROSSOVERS",
]


def test_cfg_alias():
    """Module ``cfg`` must import ``config`` for backward compatibility."""
    mod = importlib.import_module("cfg")
    assert mod is config


def test_config_exposes_paths():
    """Configuration module should expose common path variables."""
    for name in [
        "VERI_KLASORU",
        "HISSE_DOSYA_PATTERN",
        "PARQUET_ANA_DOSYA_YOLU",
        "FILTRE_DOSYA_YOLU",
    ]:
        assert hasattr(config, name)


def test_config_has_defaults():
    """Every expected constant should exist in ``config``."""
    for name in CONSTANTS:
        assert hasattr(config, name)


def test_yaml_values_loaded():
    """Values from YAML should be loaded into the module."""
    assert config.get("filter_weights", {}).get("T31") == 0.0
    assert "T31" in config.get("passive_filters", [])
