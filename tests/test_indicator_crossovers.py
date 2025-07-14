"""Unit tests for indicator crossover helpers.

These tests verify that crossover detection functions correctly identify
upward and downward movements between series.
"""

from pathlib import Path

import pandas as pd
import pytest

import config_loader
import indicator_calculator as ic


def test_add_crossovers_basic(tmp_path):
    """Add EMA-close crossover columns based on naming patterns."""
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
    """Raise ``ValueError`` for unrecognized crossover names."""
    df = pd.DataFrame({"close": [1, 2, 3]})
    with pytest.raises(ValueError):
        ic.add_crossovers(df.copy(), ["bad_crossover"])


def test_log_all_crossovers(tmp_path):
    """Write available crossover names to a log file for reference."""
    names = config_loader.load_crossover_names()
    log_path = Path("crossover_test_log.txt")
    log_path.write_text("\n".join(names))
    assert log_path.exists()
    assert names
