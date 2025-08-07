# DÜZENLENDİ – SYNTAX TEMİZLİĞİ
from __future__ import annotations

import pandas as pd

from backtest.utils import normalize_key
from backtest.data_loader import normalize_columns


def test_normalize_key_basic():
    assert normalize_key("İşlem Hacmi") == "islem_hacmi"


def test_normalize_columns_uses_common_normalize_key():
    df = pd.DataFrame({"Kapanış": [1], "İşlem Hacmi": [100]})
    normalized = normalize_columns(df)
    assert set(normalized.columns) == {"close", "volume"}
