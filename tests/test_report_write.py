import pandas as pd

import report_generator


def test_report_file_created(tmp_path):
    out = tmp_path / "t.xlsx"
    summary_df = pd.DataFrame(columns=report_generator.LEGACY_SUMMARY_COLS)
    detail_df = pd.DataFrame(columns=report_generator.LEGACY_DETAIL_COLS)
    report_generator.generate_full_report(summary_df, detail_df, [], out)
    assert out.exists() and out.stat().st_size > 0
