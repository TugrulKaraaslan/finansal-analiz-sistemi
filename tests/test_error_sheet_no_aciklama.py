import pandas as pd

from report_generator import LEGACY_DETAIL_COLS, generate_full_report


def test_error_sheet_missing_aciklama(tmp_path):
    df_sum = pd.DataFrame(
        [
            ["T1", 0, None, None, None, 0, "NO_STOCK", "", ""],
        ],
        columns=[
            "filtre_kodu",
            "hisse_sayisi",
            "ort_getiri_%",
            "en_yuksek_%",
            "en_dusuk_%",
            "islemli",
            "sebep_kodu",
            # 'sebep_aciklama' intentionally omitted
            "tarama_tarihi",
            "satis_tarihi",
        ],
    )
    df_det = pd.DataFrame(columns=LEGACY_DETAIL_COLS)
    path = tmp_path / "report.xlsx"
    generate_full_report(df_sum, df_det, [], path, keep_legacy=False)
    with pd.ExcelFile(path) as xls:
        assert "Hatalar" in xls.sheet_names
        df = pd.read_excel(xls, "Hatalar")
        assert df.loc[0, "detay"] == "-"
