import pandas as pd

import src.kontrol_araci as kontrol_araci
from finansal_analiz_sistemi.report_writer import ReportWriter
from src.preprocessor import fill_missing_business_day
from src.utils import excel_reader


def test_fill_missing_business_day():
    df = pd.DataFrame({"tarih": ["2025-03-07", None, "2025-03-10"]})
    out = fill_missing_business_day(df)
    assert out["tarih"].iloc[1] == pd.Timestamp("2025-03-07")


def test_excel_reader_cache(tmp_path):
    path = tmp_path / "t.xlsx"
    df = pd.DataFrame({"a": [1, 2]})
    df.to_excel(path, index=False)
    x1 = excel_reader.open_excel_cached(path)
    x2 = excel_reader.open_excel_cached(str(path))
    assert x1 is x2
    pd.testing.assert_frame_equal(excel_reader.read_excel_cached(path, "Sheet1"), df)
    excel_reader.clear_cache()
    assert not excel_reader._excel_cache


def test_excel_reader_cache_refresh(tmp_path):
    path = tmp_path / "t.xlsx"
    df1 = pd.DataFrame({"a": [1]})
    df1.to_excel(path, index=False)
    x1 = excel_reader.open_excel_cached(path)

    df2 = pd.DataFrame({"a": [2]})
    df2.to_excel(path, index=False)

    x2 = excel_reader.open_excel_cached(path)
    assert x1 is not x2
    pd.testing.assert_frame_equal(excel_reader.read_excel_cached(path, "Sheet1"), df2)
    excel_reader.clear_cache()


def test_tarama_denetimi_summary(monkeypatch):
    df_filtreler = pd.DataFrame({"kod": ["F1"], "PythonQuery": ["close > open"]})
    df_ind = pd.DataFrame()

    def fake_apply(df, kod, query):
        return None, {
            "kod": kod,
            "tip": "tarama",
            "durum": "OK",
            "sebep": "",
            "eksik_sutunlar": "",
            "nan_sutunlar": "",
            "secim_adedi": 0,
        }

    monkeypatch.setattr(kontrol_araci, "_apply_single_filter", fake_apply)
    result = kontrol_araci.tarama_denetimi(df_filtreler, df_ind)
    assert len(result) == 2
    assert result.iloc[-1]["kod"] == "_SUMMARY"


def test_logging_config_import(monkeypatch):
    calls = {}
    import logging

    class DummyHandler(logging.Handler):
        def __init__(self, filename, maxBytes=None, backupCount=None, encoding=None):
            super().__init__()
            calls["file"] = filename

        def setFormatter(self, fmt):
            calls["formatter"] = True

        def emit(self, record):
            pass

    import importlib
    import logging.handlers

    import src.logging_config as lc

    monkeypatch.setattr(logging.handlers, "RotatingFileHandler", DummyHandler)
    monkeypatch.setattr(lc.os, "makedirs", lambda *a, **k: None)
    importlib.reload(lc)
    assert calls["file"].endswith("run.log")


def test_report_writer_accepts_str(tmp_path):
    df = pd.DataFrame({"a": [1]})
    nested = tmp_path / "nested" / "out.xlsx"
    ReportWriter().write_report(df, str(nested))
    assert nested.exists() and nested.stat().st_size > 0
