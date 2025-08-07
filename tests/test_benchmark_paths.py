from pathlib import Path

import pytest

from backtest.benchmark import load_xu100_pct


def test_load_xu100_pct_missing_file(tmp_path):
    missing = tmp_path / "missing.csv"
    with pytest.raises(FileNotFoundError):
        load_xu100_pct(missing)
