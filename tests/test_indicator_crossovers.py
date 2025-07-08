"""Unit tests for indicator_crossovers."""

from pathlib import Path

import pandas as pd
import pytest

import config_loader
import indicator_calculator as ic


def test_add_crossovers_basic(tmp_path):
    """Test test_add_crossovers_basic."""
    df = pd.DataFrame(
        {
            "close": [1, 2, 3, 4, 5],
        }
    )
    names = ["ema_3_keser_close_yukari", "ema_3_keser_close_asagi"]
    out = ic.add_crossovers(df.copy(), names)
    for n in names:
        assert n in out.columns
        assert out[n].dtype == int


def test_add_crossovers_unknown():
    """Test test_add_crossovers_unknown."""
    df = pd.DataFrame({"close": [1, 2, 3]})
    with pytest.raises(ValueError):
        ic.add_crossovers(df.copy(), ["bad_crossover"])


def test_log_all_crossovers(tmp_path):
    """Test test_log_all_crossovers."""
    names = config_loader.load_crossover_names()
    log_path = Path("crossover_test_log.txt")
    log_path.write_text("\n".join(names))
    assert log_path.exists()
    assert names
