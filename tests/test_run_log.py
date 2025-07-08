from pathlib import Path

import pandas as pd

from report_generator import generate_full_report


def test_run_side_log(tmp_path: Path) -> None:
    """Test test_run_side_log."""
    out = tmp_path / "demo.xlsx"
    summary = pd.DataFrame(
        {
            "filtre_kodu": ["F1"],
            "ort_getiri_%": [1.0],
            "sebep_kodu": ["OK"],
        }
    )
    detail = pd.DataFrame(
        {
            "filtre_kodu": ["F1"],
            "hisse_kodu": ["AAA"],
            "getiri_yuzde": [1.0],
            "basari": ["BAŞARILI"],
        }
    )
    generate_full_report(summary, detail, [], out)
    assert out.with_suffix(".log").exists()
