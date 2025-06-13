import os, sys
after_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, after_path)

import pandas as pd
import openpyxl
import report_generator


def test_excel_report_file_size(tmp_path):
    sonuclar = []
    for i in range(20):
        sonuclar.append(
            {
                "filtre_kodu": f"F{i}",
                "hisseler": [
                    {
                        "hisse_kodu": f"H{i}",
                        "alis_fiyati": 10,
                        "satis_fiyati": 12,
                        "getiri_yuzde": 5,
                        "alis_tarihi": "01.01.2025",
                        "satis_tarihi": "02.01.2025",
                        "uygulanan_strateji": "test",
                    }
                ],
                "tarama_tarihi": "01.01.2025",
                "satis_tarihi": "02.01.2025",
                "notlar": "",
            }
        )

    path = report_generator.olustur_excel_raporu(sonuclar, tmp_path)
    assert os.path.getsize(path) < 100 * 1024


def test_uc_sekmeli_excel_yaz(tmp_path):
    df1 = pd.DataFrame({"a": [1]})
    df2 = pd.DataFrame({"b": [2]})
    df3 = pd.DataFrame({"c": [3]})

    fname = tmp_path / "multi.xlsx"
    report_generator.kaydet_uc_sekmeli_excel(str(fname), df1, df2, df3)

    wb = openpyxl.load_workbook(fname)
    assert len(wb.sheetnames) == 3
    wb.close()

