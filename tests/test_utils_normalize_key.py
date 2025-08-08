# DÜZENLENDİ – SYNTAX TEMİZLİĞİ
from __future__ import annotations

import pandas as pd
import warnings

from backtest.utils import normalize_key
from backtest.data_loader import normalize_columns


def test_normalize_key_basic():
    assert normalize_key("İşlem Hacmi") == "islem_hacmi"


def test_normalize_columns_uses_common_normalize_key():
    df = pd.DataFrame({"Kapanış": [1], "İşlem Hacmi": [100]})
    normalized = normalize_columns(df)
    assert set(normalized.columns) == {"close", "volume"}


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
        normalized = normalize_columns(df)
    assert normalized.columns.tolist() == ["close"]
    assert normalized["close"].tolist() == [1, 2]
    assert record == []
