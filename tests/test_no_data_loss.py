import pandas as pd, tempfile
from report_generator import generate_full_report, LEGACY_SUMMARY_COLS


def test_no_data_loss(tmp_path):
    # NaN'li ama silinmemesi gereken satır
    df_sum = pd.DataFrame(
        [
            {
                "filtre_kodu": "T1",
                "hisse_sayisi": None,
                "ort_getiri_%": None,
                "en_yuksek_%": None,
                "en_dusuk_%": None,
                "islemli": 0,
                "sebep_kodu": "NO_STOCK",
                "sebep_aciklama": "",
                "tarama_tarihi": "",
                "satis_tarihi": "",
            }
        ]
    )
    df_det = pd.DataFrame()
    path = tmp_path / "rapor.xlsx"
    generate_full_report(df_sum, df_det, [], path, keep_legacy=True)
    ozet = pd.read_excel(path, "Özet")
    # Satır silinmemiş olmalı
    assert len(ozet) == 1, "Satır gereksiz silindi!"
