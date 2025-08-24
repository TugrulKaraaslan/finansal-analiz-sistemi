from pathlib import Path

import pytest
import yaml

from backtest.config.schema import ColabConfig, CostsConfig, PortfolioConfig


def test_colab_config_env_override(tmp_path, monkeypatch):
    cfg = tmp_path / "c.yaml"
    excel = tmp_path / "excel"
    excel.mkdir()
    cfg.write_text('data:\n  excel_dir: "./does_not_exist"\n')
    monkeypatch.setenv("DATA_DIR", str(excel))
    c = ColabConfig.from_yaml_with_env(cfg)
    assert c.data.excel_dir == excel.resolve()


def test_costs_defaults():
    k = CostsConfig()
    assert k.commission.bps >= 0


def test_portfolio_enums():
    with pytest.raises(Exception):
        PortfolioConfig(sizing={"mode": "WRONG"})
