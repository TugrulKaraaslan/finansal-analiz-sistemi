"""Unit tests for no_data_loss."""

import pandas as pd

from report_generator import generate_full_report


def test_no_data_loss(tmp_path):
    """Report generation should preserve rows even when values are NaN."""
    # Row contains NaN but should not be dropped
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
    # Row should remain intact
    assert len(ozet) == 1, "Satır gereksiz silindi!"
