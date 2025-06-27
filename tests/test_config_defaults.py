import importlib

import config

CONSTANTS = [
    "ALIM_ZAMANI",
    "TR_HOLIDAYS_REMOVE",
    "OHLCV_MAP",
    "INDIKATOR_AD_ESLESTIRME",
    "SERIES_SERIES_CROSSOVERS",
]


def test_config_has_defaults():
    for name in CONSTANTS:
        assert hasattr(config, name)


def test_cfg_alias():
    mod = importlib.import_module("cfg")
    assert mod is config
