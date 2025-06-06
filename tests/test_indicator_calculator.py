import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
# Ensure real pandas_ta is used in this test
sys.modules.pop("pandas_ta", None)

import pandas as pd
import numpy as np

import indicator_calculator as ic


def test_classicpivots_crossover_column_exists():
    data = {
        "hisse_kodu": ["AAA"] * 30,
        "tarih": pd.date_range("2024-01-01", periods=30, freq="D"),
        "open": np.linspace(1, 30, 30),
        "high": np.linspace(1, 30, 30) + 1,
        "low": np.linspace(1, 30, 30) - 1,
        "close": np.linspace(1, 30, 30),
        "volume": np.arange(30)
    }
    df = pd.DataFrame(data)
    result = ic.hesapla_teknik_indikatorler_ve_kesisimler(df)
    assert "classicpivots_1h_p" in result.columns
    assert "close_keser_classicpivots_1h_p_yukari" in result.columns
