import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import importlib


def test_core_indicators_defined():
    cfg = importlib.import_module("config")
    assert hasattr(cfg, "CORE_INDICATORS")
    assert isinstance(cfg.CORE_INDICATORS, list)
    assert len(cfg.CORE_INDICATORS) > 0
