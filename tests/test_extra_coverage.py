"""Additional coverage tests for utility modules."""

import pandas as pd

import src.kontrol_araci as kontrol_araci
from finansal_analiz_sistemi.report_writer import ReportWriter
from src.preprocessor import fill_missing_business_day
from src.utils import excel_reader


def test_fill_missing_business_day():
    """Fill missing business days with the previous trading day."""
    df = pd.DataFrame({"tarih": ["2025-03-07", None, "2025-03-10"]})
    out = fill_missing_business_day(df)
    assert out["tarih"].iloc[1] == pd.Timestamp("2025-03-07")


def test_excel_reader_cache(tmp_path):
    """Cached ``ExcelFile`` objects should be reused across calls."""
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
    """Refresh the cache when the Excel file is modified."""
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
    """Summary row should be appended after scanning filters."""
    df_filtreler = pd.DataFrame({"kod": ["F1"], "PythonQuery": ["close > open"]})
    df_ind = pd.DataFrame()

    def fake_apply(df, kod, query):
        """Test fake_apply."""
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


def test_logging_config_import(monkeypatch, tmp_path):
    """Importing ``log_tools`` should initialize file handlers."""
    calls = {}
    import importlib
    import logging

    class DummyHandler(logging.Handler):
        """Minimal handler used to capture log file configuration."""

        def __init__(self, filename, maxBytes=None, backupCount=None, encoding=None):
            """Store log file parameters during initialization."""
            super().__init__()
            calls["file"] = filename

        def setFormatter(self, fmt):
            """Record that a formatter was configured."""
            calls["formatter"] = True

        def emit(self, record):
            """No-op ``emit`` used only for initialization testing."""
            pass

    import logging.config
    import logging.handlers

    import finansal_analiz_sistemi as fas

    monkeypatch.setattr(logging.config, "dictConfig", lambda cfg: None)
    monkeypatch.setattr(logging.handlers, "RotatingFileHandler", DummyHandler)

    importlib.reload(fas)
    lc = importlib.import_module("finansal_analiz_sistemi.log_tools")

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(lc.config, "IS_COLAB", False)
    root = logging.getLogger()
    for h in list(root.handlers):
        try:
            h.close()
        finally:
            root.removeHandler(h)
    lc.setup_logger()
    assert str(calls["file"]).endswith("rapor.log")


def test_report_writer_accepts_str(tmp_path):
    """``ReportWriter`` should accept a path string as destination."""
    df = pd.DataFrame({"a": [1]})
    nested = tmp_path / "nested" / "out.xlsx"
    ReportWriter().write_report(df, str(nested))
    assert nested.exists() and nested.stat().st_size > 0
