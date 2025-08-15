import pandas as pd
import pytest

from backtest.benchmark import load_xu100_pct


def test_alias_handling(tmp_path):
    df = pd.DataFrame({"Tarih": ["2024-01-01", "2024-01-02"], "BIST100": [100, 110]})
    xlsx = tmp_path / "bist.xlsx"
    df.to_excel(xlsx, index=False)
    series = load_xu100_pct(xlsx)
    assert len(series) == 2
    assert series.iloc[1] == pytest.approx(10.0)
