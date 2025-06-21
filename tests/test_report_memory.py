import pytest
import report_generator
import psutil
import time


@pytest.mark.slow
def test_generate_full_report_memory(tmp_path, big_df):
    base = psutil.Process().memory_info().rss
    out = tmp_path / "rep.xlsx"
    t0 = time.time()
    df1 = big_df.head(100_000).assign(
        **{
            "filtre_kodu": "F1",
            "sebep_kodu": "OK",
            "ort_getiri_%": 0.5,
            "getiri_%": 0.5,
            "basari": "OK",
        }
    )
    summary = df1.head(1)
    report_generator.generate_full_report(summary, df1, [], out)
    dt = time.time() - t0
    peak = psutil.Process().memory_info().rss
    assert dt < 90
    assert peak - base < 2 * 1024**3
