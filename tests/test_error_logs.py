import pytest
from loguru import logger

from backtest.config import load_config
from backtest.data_loader import read_excels_long


def test_read_excels_long_missing_dir_logs(tmp_path, caplog):
    missing_dir = tmp_path / "nope"
    logger.add(caplog.handler, level="ERROR")
    with pytest.raises(FileNotFoundError) as exc:
        read_excels_long(str(missing_dir))
    msg = str(exc.value)
    assert str(missing_dir) in msg
    assert "--excel-dir" in msg
    assert str(missing_dir) in caplog.text


def test_load_config_missing_logs(tmp_path, caplog):
    missing = tmp_path / "cfg.yml"
    logger.add(caplog.handler, level="ERROR")
    with pytest.raises(FileNotFoundError) as exc:
        load_config(missing)
    msg = str(exc.value)
    assert str(missing.resolve()) in msg
    assert "--config" in msg
    assert str(missing) in caplog.text
