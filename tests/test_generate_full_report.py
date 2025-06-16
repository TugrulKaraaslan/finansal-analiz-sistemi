import os
import sys
import pandas as pd
import openpyxl

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import report_generator


def test_generate_full_report_creates_files(tmp_path):
    summary = pd.DataFrame({
        "filtre_kodu": ["F1"],
        "ort_getiri_%": [1.0],
        "sebep_kodu": ["OK"],
    })
    detail = pd.DataFrame({
        "filtre_kodu": ["F1"],
        "hisse_kodu": ["AAA"],
        "getiri_yuzde": [1.0],
        "basari": ["BAŞARILI"],
    })
    sonuc = {
        "summary": summary,
        "detail": detail,
        "tarama_tarihi": "01.01.2025",
        "satis_tarihi": "02.01.2025",
    }
    out = tmp_path / "full.xlsx"
    path = report_generator.generate_full_report(sonuc, out)

    wb = openpyxl.load_workbook(path)
    assert wb.sheetnames[:3] == ["Özet", "Detay", "İstatistik"]
    assert len(wb["Özet"]._charts) > 0
    wb.close()
