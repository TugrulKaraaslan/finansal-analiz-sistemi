from types import SimpleNamespace

import pandas as pd

from backtest.data_loader import read_excels_long


class _DummyExcelFile:
    def __init__(self, *args, **kwargs):
        self.sheet_names = ["S1"]
        self.closed = False

    def __enter__(self):
        return self

    def __exit__(self, _exc_type, _exc, _tb):
        self.closed = True

    def parse(self, sheet_name, header=0):
        _ = sheet_name, header
        return pd.DataFrame(
            {
                "Tarih": ["2024-01-01"],
                "Açılış": [1],
                "Yüksek": [2],
                "Düşük": [0.5],
                "Fiyat": [1.5],
                "Adet": [100],
            }
        )


class _StdExcelFile(_DummyExcelFile):
    def parse(self, sheet_name, header=0):  # type: ignore[override]
        _ = sheet_name, header
        return pd.DataFrame(
            {
                "date": ["2024-01-01"],
                "open": [1],
                "high": [2],
                "low": [0.5],
                "close": [1.5],
                "volume": [100],
            }
        )


def test_read_excels_long_price_schema(tmp_path, monkeypatch):
    (tmp_path / "a.xlsx").write_text("dummy")
    cfg = SimpleNamespace(
        data=SimpleNamespace(
            excel_dir=tmp_path,
            price_schema={
                "date": ["Tarih"],
                "open": ["Açılış"],
                "high": ["Yüksek"],
                "low": ["Düşük"],
                "close": ["Fiyat"],
                "volume": ["Adet"],
            },
        )
    )
    monkeypatch.setattr(pd, "ExcelFile", _DummyExcelFile)
    out = read_excels_long(cfg)
    assert "close" in out.columns and out.loc[0, "close"] == 1.5


def test_read_excels_long_closes_files(tmp_path, monkeypatch):
    (tmp_path / "a.xlsx").write_text("dummy")
    instances = []

    def _factory(*args, **kwargs):
        inst = _StdExcelFile(*args, **kwargs)
        instances.append(inst)
        return inst

    monkeypatch.setattr(pd, "ExcelFile", _factory)
    cfg = SimpleNamespace(data=SimpleNamespace(excel_dir=tmp_path))
    read_excels_long(cfg)
    assert instances and all(inst.closed for inst in instances)
