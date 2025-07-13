"""Unit tests for filtre_dogrulama."""

import os
import sys

import pandas as pd
import pytest

from filtre_dogrulama import dogrula_filtre_dataframe, validate

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


def test_invalid_filter_code_characters():
    """Validation should reject filter codes with invalid characters."""
    df = pd.DataFrame([{"flag": "BAD#", "query": "True"}])
    result = dogrula_filtre_dataframe(df)
    assert "BAD#" in result
    assert "Geçersiz" in result["BAD#"]  # message contains "Invalid characters"


def test_empty_python_query():
    """Empty query strings should produce an error message."""
    df = pd.DataFrame([{"flag": "VALID", "query": ""}])
    result = dogrula_filtre_dataframe(df)
    assert "VALID" in result
    assert "Query" in result["VALID"]


def test_missing_python_query_value():
    """Ensure ``NA`` query values are reported as missing."""
    df = pd.DataFrame([{"flag": "VALID", "query": pd.NA}])
    result = dogrula_filtre_dataframe(df)
    assert "VALID" in result
    assert "Query" in result["VALID"]


def test_nan_flag_value():
    """Missing ``flag`` values should produce a row-level error."""
    df = pd.DataFrame([{"flag": pd.NA, "query": "True"}])
    result = dogrula_filtre_dataframe(df)
    assert "satir_0" in result
    assert "flag" in result["satir_0"]


def test_missing_columns_raises_keyerror():
    """Raise ``KeyError`` when required columns are absent."""
    df = pd.DataFrame([{"FilterCode": "F1", "PythonQuery": "True"}])
    with pytest.raises(KeyError):
        dogrula_filtre_dataframe(df)


def test_validate_reports_missing_flag():
    """Validation should mark records with missing flags."""
    df = pd.DataFrame([{"flag": pd.NA, "query": "True"}])
    errors = validate(df)
    assert len(errors) == 1
    assert errors[0].hata_tipi == "MISSING_FLAG"


def test_validate_reports_invalid_flag_characters():
    """Report invalid characters detected in flag values."""
    df = pd.DataFrame([{"flag": "BAD#", "query": "True"}])
    errors = validate(df)
    assert any(e.hata_tipi == "INVALID_FLAG" for e in errors)


def test_validate_reports_missing_query():
    """Detect filters where the query expression is empty."""
    df = pd.DataFrame([{"flag": "VALID", "query": ""}])
    errors = validate(df)
    assert any(e.hata_tipi == "MISSING_QUERY" for e in errors)
