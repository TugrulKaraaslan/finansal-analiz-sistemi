import os, sys
after_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, after_path)

import pandas as pd

import report_generator


def test_detayli_rapor_contains_new_fields(tmp_path):
    sonuclar = [{
        "filtre_kodu": "F1",
        "hisseler": [
            {
                "hisse_kodu": "AAA",
                "alis_fiyati": 10,
                "satis_fiyati": 12,
                "getiri_yuzde": 20,
                "alis_tarihi": "07.03.2025",
                "satis_tarihi": "10.03.2025",
                "uygulanan_strateji": "basit_backtest"
            }
        ],
        "tarama_tarihi": "07.03.2025",
        "satis_tarihi": "10.03.2025",
        "notlar": ""
    }]
    path = report_generator.olustur_hisse_bazli_rapor(sonuclar, tmp_path)
    df = pd.read_csv(path)
    assert {"alis_tarihi", "satis_tarihi", "uygulanan_strateji"}.issubset(df.columns)

