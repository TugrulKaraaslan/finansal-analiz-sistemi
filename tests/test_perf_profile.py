import os
import sys
import pandas as pd
import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import indicator_calculator as ic  # noqa: E402


def test_ema_columns_notna():
    dates = pd.date_range("2024-01-01", periods=10, freq="D")
    df = pd.DataFrame(
        {
            "hisse_kodu": ["AAA"] * 10,
            "tarih": dates,
            "open": np.arange(10) + 1,
            "high": np.arange(10) + 1,
            "low": np.arange(10) + 1,
            "close": np.arange(10) + 1,
            "volume": np.arange(10) + 1,
        }
    )

    result = ic.hesapla_teknik_indikatorler_ve_kesisimler(df)
    assert result["ema_5"].notna().all()
