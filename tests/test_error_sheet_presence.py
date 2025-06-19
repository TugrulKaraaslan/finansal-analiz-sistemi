import os
import sys
import pandas as pd

# Proje kök dizinini PYTHONPATH'e ekle
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from report_generator import (
    generate_full_report,
    LEGACY_SUMMARY_COLS,
    LEGACY_DETAIL_COLS,
)


def test_hatalar_sheet_not_empty_and_matches(tmp_path):
    # -- 1. Örnek veri seti: 5 satır → 2 OK, 1 QUERY_ERROR, 2 NO_STOCK
    df_sum = pd.DataFrame(
        [
            ["T1", 1, 2.0, 2, -1, 1, "OK", "", "", ""],
            ["T2", 0, None, None, None, 0, "NO_STOCK", "", "", ""],
            ["T3", 0, None, None, None, 0, "QUERY_ERROR", "", "", ""],
            ["T4", 0, None, None, None, 0, "NO_STOCK", "", "", ""],
            ["T5", 2, 10.0, 15, -2, 1, "OK", "", "", ""],
        ],
        columns=[
            "filtre_kodu",
            "hisse_sayisi",
            "ort_getiri_%",
            "en_yuksek_%",
            "en_dusuk_%",
            "islemli",
            "sebep_kodu",
            "sebep_aciklama",
            "tarama_tarihi",
            "satis_tarihi",
        ],
    )

    # -- Detay dummy
    df_det = pd.DataFrame(columns=LEGACY_DETAIL_COLS)

    # -- Hata listesi (QUERY_ERROR satırı)
    err_list = [
        {
            "filtre_kodu": "T3",
            "hata_tipi": "QUERY_ERROR",
            "detay": "demo parse hatası",
            "cozum_onerisi": "ifade düzelt",
        }
    ]

    path = tmp_path / "rapor.xlsx"
    generate_full_report(df_sum, df_det, err_list, path, keep_legacy=True)

    with pd.ExcelFile(path) as xls:
        assert "Hatalar" in xls.sheet_names, "'Hatalar' sheet'i yok!"

        hatalar_df = pd.read_excel(xls, "Hatalar")
        assert not hatalar_df.empty, "'Hatalar' sheet'i boş!"

        # Özet’te OK olmayan satır sayısı == Hatalar sheet satır sayısı
        ozet_df = pd.read_excel(xls, "Özet")
        n_bad = (ozet_df["sebep_kodu"] != "OK").sum()
        assert len(hatalar_df) == n_bad, "Hatalar sayısı uyumsuz!"
