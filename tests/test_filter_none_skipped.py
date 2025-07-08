import sys
import types

import pandas as pd


def test_filter_none_skipped(tmp_path, monkeypatch):
    import logging

    dummy = types.SimpleNamespace(
        get_logger=logging.getLogger,
        setup_logging=lambda: logging.getLogger(),
    )
    monkeypatch.setitem(sys.modules, "finansal_analiz_sistemi.logging_config", dummy)

    from finansal_analiz_sistemi.data_loader import yukle_filtre_dosyasi

    df = pd.DataFrame({"filtre_kodu": ["F1", "", None], "min": ["1", "2", "3"]})
    p = tmp_path / "f.csv"
    df.to_csv(p, sep=";", index=False)
    out = yukle_filtre_dosyasi(p)
    assert list(out["filtre_kodu"]) == ["F1"]
    assert out["min"].dtype.kind in "fi"
