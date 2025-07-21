"""Tests for ``_build_detay_df`` ensuring detail frames are populated."""

import pandas as pd

from report_generator import _build_detay_df


def test_detay_not_empty():
    """Detail report should remain populated after merge operations."""
    trades = pd.DataFrame(
        {
            "filtre_kodu": ["F1", "F1"],
            "hisse_kodu": ["AAA", "BBB"],
            "getiri_%": [5.0, -2.0],
            "basari": ["BAŞARILI", "BAŞARISIZ"],
            "strateji": ["S", "S"],
            "sebep_kodu": ["OK", "OK"],
        }
    )
    detay_list = [
        pd.DataFrame({"filtre_kodu": ["F1"], "hisse_kodu": ["AAA"]}),
        pd.DataFrame({"filtre_kodu": ["F1"], "hisse_kodu": ["BBB"]}),
    ]
    detay_df = _build_detay_df(detay_list, trades)
    critical = ["hisse_kodu", "getiri_%", "basari", "strateji", "sebep_kodu"]
    # ensure none of the critical columns contain missing values
    assert detay_df[critical].notna().all().all()


def test_detay_empty_list():
    """Empty input should yield an empty DataFrame with expected columns."""
    trades = pd.DataFrame(
        {
            "filtre_kodu": ["F1"],
            "hisse_kodu": ["AAA"],
            "getiri_%": [5.0],
            "basari": ["BAŞARILI"],
            "strateji": ["S"],
            "sebep_kodu": ["OK"],
        }
    )
    df = _build_detay_df([], trades)
    assert df.empty
    assert list(df.columns) == list(trades.columns)


def test_detay_none_trades():
    """Passing ``None`` as trades should not raise and return empty frame."""
    out = _build_detay_df([], None)
    assert out.empty and list(out.columns) == []
