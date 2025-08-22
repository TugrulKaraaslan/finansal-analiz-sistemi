from __future__ import annotations

import pandas as pd
import pandera as pa
import pytest

from backtest.naming import (
    normalize_name,
    validate_columns_schema,
    canonicalize_columns,
)


def test_alias_normalization_basic():
    pairs = {
        "EMA20": "ema_20",
        "CLOSE": "close",
        "RSI14": "rsi_14",
        "ITS_9": "ichimoku_conversionline",
        "STOCHk_14_3_3.1": "stoch_k",
        "MACD_12_26_9.1": "macd_12_26_9",
        "change_1_w_percent": "change_1w_percent",
    }
    for raw, want in pairs.items():
        assert normalize_name(raw) == want


def test_snake_case_enforcement():
    assert normalize_name("ema20") == "ema_20"
    with pytest.raises(ValueError):
        normalize_name("???")


def test_pandera_strict_mode():
    df = pd.DataFrame({"DATE": ["2024-01-01"], "CLOSE": [1.5], "ema2O": [1.0]})
    with pytest.raises(pa.errors.SchemaError):
        validate_columns_schema(df, mode="strict_fail")


def test_auto_fix_mode():
    df = pd.DataFrame(
        {
            "DATE": ["2024-01-01"],
            "OPEN": [1.0],
            "HIGH": [2.0],
            "LOW": [0.5],
            "CLOSE": [1.5],
            "VOLUME": [100],
            "ema2O": [1.0],
        }
    )
    fixed, skipped = validate_columns_schema(df, mode="auto_fix")
    assert skipped == ["ema_2_o"]
    assert "close" in fixed.columns
    assert "ema_2_o" not in fixed.columns


def test_canonicalize_columns_drops_duplicates():
    df = pd.DataFrame(
        {
            "BBM_20_2": [1, 2, 3],
            "bbm_20_2": [1, 2, 3],
        }
    )
    out = canonicalize_columns(df)
    assert list(out.columns) == ["bbm_20_2"]
