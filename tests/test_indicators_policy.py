import logging

import pandas as pd
import pytest

from backtest.config import load_config
from backtest.indicators import compute_indicators
from tests.utils.tmp_filter_module import write_tmp_filters_module


def test_indicators_engine_none_is_default_and_locked(tmp_path):
    mod = write_tmp_filters_module(
        tmp_path,
        [{"FilterCode": "F", "PythonQuery": "close>0"}],
    )
    cfg_txt = f"""
project:
  out_dir: "{tmp_path}"
  run_mode: "range"
  start_date: "2024-01-01"
  end_date: "2024-01-02"
  holding_period: 1
  transaction_cost: 0.0

data:
  excel_dir: "{tmp_path}"
filters:
  module: {mod}
  include: ["*"]
"""
    cfg_path = tmp_path / "cfg.yaml"
    cfg_path.write_text(cfg_txt, encoding="utf-8")
    cfg = load_config(cfg_path)
    assert cfg.indicators.engine == "none"

    bad = cfg_txt + "indicators:\n  engine: pandas_ta\n"
    bad_path = tmp_path / "bad.yaml"
    bad_path.write_text(bad, encoding="utf-8")
    with pytest.raises(ValueError):
        load_config(bad_path)


def test_compute_indicators_noop_when_engine_none(caplog):
    df = pd.DataFrame({"a": [1, 2, 3]})
    with caplog.at_level(logging.INFO, logger="backtest.indicators"):
        res = compute_indicators(df, params={})
    assert res is df
    assert "indicators: engine=none" in caplog.text


def test_engine_override_raises():
    df = pd.DataFrame({"a": [1]})
    with pytest.raises(ValueError):
        compute_indicators(df, engine="pandas_ta")
