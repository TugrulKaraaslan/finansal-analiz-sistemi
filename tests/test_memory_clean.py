import pytest
import os
from pathlib import Path

import pandas as pd
import run as main
import filter_engine as fe
import utils.failure_tracker as ft

psutil = pytest.importorskip("psutil")


def test_memory_clean(tmp_path, monkeypatch):
    mp_file = Path("reports/memory_profile.csv")
    if mp_file.exists():
        mp_file.unlink()

    monkeypatch.setattr(
        main,
        "veri_yukle",
        lambda force_excel_reload_param=False: (pd.DataFrame(), pd.DataFrame()),
    )
    monkeypatch.setattr(main, "on_isle", lambda df: df)

    def fake_ind(df):
        from utils.memory_profile import mem_profile

        with mem_profile():
            return df

    monkeypatch.setattr(main, "indikator_hesapla", fake_ind)
    monkeypatch.setattr(main, "filtre_uygula", lambda df, tarama_tarihi: ({}, {}))
    monkeypatch.setattr(
        main,
        "backtest_yap",
        lambda df, filtre_sonuclari, tarama_tarihi_str, satis_tarihi_str: (
            pd.DataFrame(),
            pd.DataFrame(),
        ),
    )

    def fake_rapor(summary, detail):
        from utils.memory_profile import mem_profile

        with mem_profile():
            pass

    monkeypatch.setattr(main, "raporla", fake_rapor)

    base = psutil.Process(os.getpid()).memory_info().rss
    for _ in range(2):
        main.calistir_tum_sistemi("2025-03-07", "2025-03-10")
        assert not fe.FAILED_FILTERS
        assert not ft.failures

    peak = max(int(line.split(",")[1]) for line in open(mp_file))
    assert peak - base < 8 * 1024**3
