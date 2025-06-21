import pytest
import report_generator
import pandas as pd
import psutil
import time


@pytest.mark.slow
def test_generate_full_report_memory(tmp_path, big_df):
    base = psutil.Process().memory_info().rss
    out = tmp_path / "rep.xlsx"
    t0 = time.time()
    # minimal meta row expected by generate_full_report
    summary = pd.DataFrame(
        {
            "filtre_kodu": ["F1"],
            "tarih": [pd.Timestamp.now()],
            "sebep_kodu": ["OK"],
            "ort_getiri_%": [0.0],
            "getiri_%": [0.0],
            "basari": ["OK"],
        }
    )

    report_generator.generate_full_report(summary, big_df.head(100_000), [], out)
    dt = time.time() - t0
    peak = psutil.Process().memory_info().rss
    assert dt < 90
    assert peak - base < 2 * 1024**3
