"""Test module for test_kpi_pct_inflate."""

import pandas as pd

from report_stats import build_stats_df


def test_kpi_pct_inflate():
    """Test test_kpi_pct_inflate."""
    df = pd.DataFrame(
        {
            "filtre_kodu": ["F"],
            "hisse_sayisi": [1],
            "ort_getiri_%": [12.8],
            "en_yuksek_%": [12.8],
            "en_dusuk_%": [12.8],
            "islemli": ["EVET"],
            "sebep_kodu": ["OK"],
            "sebep_aciklama": [""],
            "tarama_tarihi": ["x"],
            "satis_tarihi": ["x"],
        }
    )
    stats = build_stats_df(df)
    assert stats["genel_ortalama_%"].iat[0] == 12.8
