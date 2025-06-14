import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pandas as pd

from filtre_dogrulama import dogrula_filtre_dataframe


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


def test_missing_python_query():
    df = pd.DataFrame([{"flag": "VALID"}])
    result = dogrula_filtre_dataframe(df)
    assert "VALID" in result
    assert "Query" in result["VALID"]
