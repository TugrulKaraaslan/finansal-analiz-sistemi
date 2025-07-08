import os
import sys

import pandas as pd

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import backtest_core  # noqa: E402
from src.preprocessor import fill_missing_business_day  # noqa: E402


def test_get_fiyat_moves_to_next_date():
    """Test test_get_fiyat_moves_to_next_date."""
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


def test_fill_missing_business_day_shifts_nat():
    """Test test_fill_missing_business_day_shifts_nat."""
    raw = pd.DataFrame(
        {
            "tarih": [pd.NaT, pd.to_datetime("11.03.2025", dayfirst=True)],
            "close": [10.0, 11.0],
        }
    )

    out = fill_missing_business_day(raw, date_col="tarih")

    assert out.loc[0, "tarih"] == pd.to_datetime("10.03.2025", dayfirst=True)
