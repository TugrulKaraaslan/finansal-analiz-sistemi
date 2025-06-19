from report_generator import generate_full_report, LEGACY_SUMMARY_COLS
import os
import sys
import pandas as pd

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


def test_stats_values(tmp_path):
    df = pd.DataFrame(
        {
            "filtre_kodu": ["T1", "T2", "T3"],
            "hisse_sayisi": [1, 0, 0],
            "ort_getiri_%": [2.0, None, None],
            "en_yuksek_%": [2, 0, 0],
            "en_dusuk_%": [-1, 0, 0],
            "islemli": [1, 0, 0],
            "sebep_kodu": ["OK", "NO_STOCK", "QUERY_ERROR"],
            "sebep_aciklama": ["", "", ""],
            "tarama_tarihi": ["x", "x", "x"],
            "satis_tarihi": ["x", "x", "x"],
        }
    )
    path = tmp_path / "stats.xlsx"
    generate_full_report(df, pd.DataFrame(columns=[]), [], path, keep_legacy=True)
    st = pd.read_excel(path, "İstatistik").iloc[0]
    assert st["toplam_filtre"] == 3
    assert st["islemli"] == 1
    assert st["işlemsiz"] == 1
    assert st["hatalı"] == 1
    assert st["genel_başarı_%"] == 33.33
    assert st["genel_ortalama_%"] == 2.0
