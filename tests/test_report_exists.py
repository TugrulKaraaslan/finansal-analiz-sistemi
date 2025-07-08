"""Unit tests for report_exists."""

import pandas as pd

import run as main_mod
from finansal_analiz_sistemi.main import calistir_tum_sistemi


def test_report_file_created(tmp_path, monkeypatch):
    """Verify that ``calistir_tum_sistemi`` writes an Excel report."""
    out = tmp_path / "test.xlsx"

    # Stub dependencies to avoid heavy operations
    monkeypatch.setattr(
        main_mod,
        "veri_yukle",
        lambda force_excel_reload_param=False: (pd.DataFrame(), pd.DataFrame()),
    )
    monkeypatch.setattr(main_mod, "on_isle", lambda df: df)
    monkeypatch.setattr(main_mod, "indikator_hesapla", lambda df: df)
    monkeypatch.setattr(main_mod, "filtre_uygula", lambda df, tarama_tarihi: ({}, {}))

    def fake_backtest(df, filtre_sonuclari, tarama_tarihi_str, satis_tarihi_str):
        """Return minimal summary and detail frames for backtest stubbing."""
        summary = pd.DataFrame(
            {
                "filtre_kodu": ["F1"],
                "hisse_sayisi": [1],
                "ort_getiri_%": [0.1],
                "sebep_kodu": ["OK"],
            }
        )
        detail = pd.DataFrame(
            {
                "filtre_kodu": ["F1"],
                "hisse_kodu": ["AAA"],
                "getiri_%": [0.1],
                "basari": ["EVET"],
            }
        )
        return summary, detail

    monkeypatch.setattr(main_mod, "backtest_yap", fake_backtest)

    calistir_tum_sistemi("2025-03-07", "2025-03-10", output_path=out, logger_param=None)
    assert out.exists() and out.stat().st_size > 0
