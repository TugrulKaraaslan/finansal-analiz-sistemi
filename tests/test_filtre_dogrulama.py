from filtre_dogrulama import dogrula_filtre_dataframe
import pytest
import pandas as pd
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


def test_invalid_filter_code_characters():
    df = pd.DataFrame([{"flag": "BAD#", "query": "True"}])
    result = dogrula_filtre_dataframe(df)
    assert "BAD#" in result
    assert "Geçersiz" in result["BAD#"]  # message contains "Geçersiz karakterler"


def test_empty_python_query():
    df = pd.DataFrame([{"flag": "VALID", "query": ""}])
    result = dogrula_filtre_dataframe(df)
    assert "VALID" in result
    assert "Query" in result["VALID"]


def test_missing_python_query_value():
    df = pd.DataFrame([{"flag": "VALID", "query": pd.NA}])
    result = dogrula_filtre_dataframe(df)
    assert "VALID" in result
    assert "Query" in result["VALID"]


def test_nan_flag_value():
    df = pd.DataFrame([{"flag": pd.NA, "query": "True"}])
    result = dogrula_filtre_dataframe(df)
    assert "satir_0" in result
    assert "flag" in result["satir_0"]


def test_missing_columns_raises_keyerror():
    df = pd.DataFrame([{"FilterCode": "F1", "PythonQuery": "True"}])
    with pytest.raises(KeyError):
        dogrula_filtre_dataframe(df)
