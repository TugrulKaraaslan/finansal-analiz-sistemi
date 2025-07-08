"""Test module for test_report_memory."""

import time

import pandas as pd
import psutil
import pytest

import report_generator


@pytest.mark.slow
def test_generate_full_report_memory(tmp_path, big_df):
    """Test test_generate_full_report_memory."""
    base = psutil.Process().memory_info().rss
    out = tmp_path / "rep.xlsx"
    t0 = time.time()
    # minimal meta row expected by generate_full_report
    summary = pd.DataFrame([{c: pd.NA for c in report_generator.LEGACY_SUMMARY_COLS}])
    summary.loc[0, ["filtre_kodu", "tarih", "sebep_kodu"]] = [
        "F1",
        pd.Timestamp.now(),
        "OK",
    ]

    report_generator.generate_full_report(summary, big_df.head(100_000), [], out)
    dt = time.time() - t0
    peak = psutil.Process().memory_info().rss
    assert dt < 90
    assert peak - base < 2 * 1024**3
