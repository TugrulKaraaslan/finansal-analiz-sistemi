from pathlib import Path

import pytest
import yaml

from backtest.strategy import StrategyRegistry


def test_load_from_yaml(tmp_path):
    cfg = {"strategies": [{"id": "s1", "filters": ["T1"], "params": {"risk": 1}}]}
    p = tmp_path / "s.yaml"
    p.write_text(yaml.safe_dump(cfg))
    reg, constraints = StrategyRegistry.load_from_file(p)
    assert reg.get("s1").filters == ["T1"]
    assert constraints == {}


def test_unknown_filter(tmp_path):
    cfg = {"strategies": [{"id": "bad", "filters": ["BAD"]}]}
    p = tmp_path / "bad.yaml"
    p.write_text(yaml.safe_dump(cfg))
    with pytest.raises(ValueError):
        StrategyRegistry.load_from_file(p)
