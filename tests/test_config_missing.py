# DÜZENLENDİ – SYNTAX TEMİZLİĞİ
import pytest

from backtest.config import load_config


def test_load_config_missing_file(tmp_path):
    missing = tmp_path / "nonexistent.yml"
    with pytest.raises(FileNotFoundError):
        load_config(missing)
