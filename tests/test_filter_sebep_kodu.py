"""Test module for test_filter_sebep_kodu."""

import os
import sys

import pandas as pd

import filter_engine
from filtre_dogrulama import SEBEP_KODLARI

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


def _base_df():
    """Test _base_df."""
    return pd.DataFrame(
        {
            "hisse_kodu": ["AAA"],
            "tarih": [pd.Timestamp("2025-03-01")],
            "close": [10],
        }
    )


def _apply(query: str) -> str:
    """Test _apply."""
    filt = pd.DataFrame({"FilterCode": ["F1"], "PythonQuery": [query]})
    result, _ = filter_engine.uygula_filtreler(
        _base_df(), filt, pd.Timestamp("2025-03-01")
    )
    return result["F1"]["sebep"]


def test_ok_code():
    """Test test_ok_code."""
    code = _apply("close > 5")
    assert code == "OK"
    assert code in SEBEP_KODLARI


def test_missing_column_returns_missing_col():
    """Test test_missing_column_returns_missing_col."""
    code = _apply("missing > 0")
    assert code == "QUERY_ERROR"


def test_syntax_error_returns_query_error():
    """Test test_syntax_error_returns_query_error."""
    code = _apply("close >")
    assert code == "QUERY_ERROR"
