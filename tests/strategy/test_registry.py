import pytest
import pandas as pd
import yaml

from backtest.strategy import StrategyRegistry


def test_load_from_yaml(tmp_path):
    cfg = {
        "strategies": [
            {
                "id": "s1",
                "filters": ["T1"],
                "params": {"risk": 1},
            }
        ]
    }
    p = tmp_path / "s.yaml"
    p.write_text(yaml.safe_dump(cfg))
    filters_df = pd.DataFrame({"FilterCode": ["T1"], "PythonQuery": ["close>0"]})
    reg, constraints = StrategyRegistry.load_from_file(p, filters_df)
    assert reg.get("s1").filters == ["T1"]
    assert constraints == {}


def test_unknown_filter(tmp_path):
    cfg = {"strategies": [{"id": "bad", "filters": ["BAD"]}]}
    p = tmp_path / "bad.yaml"
    p.write_text(yaml.safe_dump(cfg))
    filters_df = pd.DataFrame({"FilterCode": ["T1"], "PythonQuery": ["close>0"]})
    with pytest.raises(ValueError):
        StrategyRegistry.load_from_file(p, filters_df)
