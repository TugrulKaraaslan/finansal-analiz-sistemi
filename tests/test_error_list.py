import pandas as pd

from report_generator import LEGACY_SUMMARY_COLS, generate_full_report


def test_error_list_writes_sheet(tmp_path):
    errs = [
        {
            "filtre_kodu": "T1",
            "hata_tipi": "QUERY_ERROR",
            "detay": "demo",
            "cozum_onerisi": "fix",
        }
    ]
    path = tmp_path / "err.xlsx"
    generate_full_report(
        pd.DataFrame(columns=LEGACY_SUMMARY_COLS),
        pd.DataFrame(columns=[]),
        errs,
        path,
        keep_legacy=True,
    )
    with pd.ExcelFile(path) as xls:
        assert "Hatalar" in xls.sheet_names
