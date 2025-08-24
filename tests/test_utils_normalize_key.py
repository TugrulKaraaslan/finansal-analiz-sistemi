from __future__ import annotations

import warnings

import pandas as pd

from backtest.data_loader import normalize_columns
from backtest.utils import normalize_key


def test_normalize_key_basic():
    assert normalize_key("İşlem Hacmi") == "islem_hacmi"


def test_normalize_key_nan():
    assert normalize_key(float("nan")) == ""


def test_normalize_columns_uses_common_normalize_key():
    df = pd.DataFrame({"Kapanış": [1], "İşlem Hacmi": [100]})
    normalized, colmap = normalize_columns(df)
    assert "close" in normalized.columns
    assert "volume" in normalized.columns
    assert colmap["close"] == "Kapanış"
    assert colmap["volume"] == "İşlem Hacmi"


def test_normalize_columns_drops_duplicate_aliases_without_warning():
    df = pd.DataFrame(
        {
            "close": [1, 2],
            "kapanis": [3, 4],
            "kapanış": [5, 6],
        }
    )
    with warnings.catch_warnings(record=True) as record:
        warnings.simplefilter("error")
        normalized, colmap = normalize_columns(df)
    assert "close" in normalized.columns
    assert colmap["close"] == "close"
    assert record == []
