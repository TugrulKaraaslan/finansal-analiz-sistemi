"""Unit tests for normalize."""

import pandas as pd

from finansal_analiz_sistemi.utils.normalize import normalize_filtre_kodu


def test_normalize_handles_spaces_and_case():
    """Column names with spaces or case differences should normalize cleanly."""
    df = pd.DataFrame({" FilterCode ": ["F1"]})
    out = normalize_filtre_kodu(df)
    assert list(out.columns) == ["filtre_kodu"]
    assert out["filtre_kodu"].tolist() == ["F1"]


def test_normalize_removes_duplicate_aliases():
    """Duplicate alias columns must collapse into a single ``filtre_kodu``."""
    df = pd.DataFrame({"FilterCode": ["F1"], "filtercode ": ["F1"]})
    out = normalize_filtre_kodu(df)
    assert list(out.columns) == ["filtre_kodu"]
    assert out["filtre_kodu"].tolist() == ["F1"]
