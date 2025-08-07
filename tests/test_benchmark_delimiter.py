from pathlib import Path

import pandas as pd
import pytest

from backtest.benchmark import load_xu100_pct


def test_load_xu100_pct_semicolon_decimal_comma(tmp_path):
    csv_file = tmp_path / "xu100.csv"
    csv_file.write_text(
        "Date;Close\n2020-01-01;100,0\n2020-01-02;110,0\n", encoding="utf-8"
    )
    series = load_xu100_pct(csv_file)
    assert len(series) == 2
    assert series.iloc[1] == pytest.approx(10.0)
