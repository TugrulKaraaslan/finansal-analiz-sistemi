import pandas as pd
import pytest
from loguru import logger

from backtest.benchmark import BenchmarkLoader


def test_load_excel(tmp_path, caplog):
    df = pd.DataFrame({"date": ["2024-01-01", "2024-01-02"], "close": [100, 110]})
    path = tmp_path / "bist.xlsx"
    df.to_excel(path, sheet_name="BIST", index=False)
    cfg = {
        "source": "excel",
        "excel_path": str(path),
        "excel_sheet": "BIST",
        "column_date": "date",
        "column_close": "close",
    }
    with caplog.at_level("INFO"):
        logger.add(caplog.handler, level="INFO")
        loaded = BenchmarkLoader(cfg).load()
    assert list(loaded.columns) == ["date", "close"]
    assert len(loaded) == 2
    assert "benchmark loaded rows=2" in caplog.text


def test_load_csv(tmp_path):
    df = pd.DataFrame({"date": ["2024-01-01", "2024-01-02"], "close": [1, 2]})
    path = tmp_path / "bist.csv"
    df.to_csv(path, index=False)
    cfg = {
        "source": "csv",
        "csv_path": str(path),
        "column_date": "date",
        "column_close": "close",
    }
    loaded = BenchmarkLoader(cfg).load()
    assert len(loaded) == 2


def test_load_none():
    cfg = {"source": "none"}
    assert BenchmarkLoader(cfg).load() is None


def test_missing_excel(tmp_path):
    cfg = {"source": "excel", "excel_path": str(tmp_path / "missing.xlsx")}
    with pytest.raises(FileNotFoundError):
        BenchmarkLoader(cfg).load()
