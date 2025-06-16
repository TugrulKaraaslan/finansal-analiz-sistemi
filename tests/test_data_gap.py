import os
import sys
import pandas as pd

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import backtest_core


def test_get_fiyat_moves_to_next_date():
    df = pd.DataFrame(
        {
            "hisse_kodu": ["AAA", "AAA"],
            "tarih": [
                pd.to_datetime("09.03.2025", dayfirst=True),
                pd.to_datetime("11.03.2025", dayfirst=True),
            ],
            "close": [10.0, 11.0],
        }
    )

    fiyat = backtest_core._get_fiyat(
        df, pd.to_datetime("10.03.2025", dayfirst=True), "close"
    )
    assert fiyat == 11.0
