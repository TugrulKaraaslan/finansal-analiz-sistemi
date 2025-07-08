import importlib

from finansal_analiz_sistemi import config

CONSTANTS = [
    "ALIM_ZAMANI",
    "TR_HOLIDAYS_REMOVE",
    "OHLCV_MAP",
    "INDIKATOR_AD_ESLESTIRME",
    "SERIES_SERIES_CROSSOVERS",
]


def test_config_has_defaults():
    """Test test_config_has_defaults."""
    for name in CONSTANTS:
        assert hasattr(config, name)


def test_cfg_alias():
    """Test test_cfg_alias."""
    mod = importlib.import_module("cfg")
    assert mod is config


def test_yaml_values_loaded():
    """YAML'deki değerler modüle yüklenmeli."""
    assert config.get("filter_weights", {}).get("T31") == 0.0
    assert "T31" in config.get("passive_filters", [])


def test_config_exposes_paths():
    """Test test_config_exposes_paths."""
    for name in [
        "VERI_KLASORU",
        "HISSE_DOSYA_PATTERN",
        "PARQUET_ANA_DOSYA_YOLU",
        "FILTRE_DOSYA_YOLU",
    ]:
        assert hasattr(config, name)
