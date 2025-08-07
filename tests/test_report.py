from __future__ import annotations

import warnings
import pandas as pd

from backtest.report import drop_inactive_filters


def test_drop_inactive_filters_writes_file_and_warns(tmp_path):
    df = pd.DataFrame({
        "FilterCode": ["t1", "t2", "t3"],
        "trade_count": [5, 0, 3],
        "extra": [1, 2, 3],
    })
    out_dir = tmp_path / "raporlar"
    with warnings.catch_warnings(record=True) as w:
        filtered = drop_inactive_filters(df, out_dir)
        assert filtered["FilterCode"].tolist() == ["t1", "t3"]
        inactive_file = out_dir / "inactive_filters.txt"
        assert inactive_file.exists()
        assert inactive_file.read_text(encoding="utf-8").strip() == "t2"
        assert any("t2" in str(wi.message) for wi in w)


def test_drop_inactive_filters_no_inactive(tmp_path):
    df = pd.DataFrame({
        "FilterCode": ["t1", "t2"],
        "trade_count": [1, 2],
    })
    out_dir = tmp_path / "raporlar"
    with warnings.catch_warnings(record=True) as w:
        filtered = drop_inactive_filters(df, out_dir)
        assert filtered.equals(df)
        assert not (out_dir / "inactive_filters.txt").exists()
        assert w == []
