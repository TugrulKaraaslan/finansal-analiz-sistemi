import os
import sys

import pandas as pd

import filter_engine

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


def test_t17_t500_ok():
    """Test test_t17_t500_ok."""
    df = pd.DataFrame(
        {
            "hisse_kodu": ["AAA"],
            "tarih": [pd.Timestamp("2025-03-07")],
            "relative_volume": [1.4],
            "change_1w_percent": [10.0],
            "sma_10_keser_sma_50_yukari": [True],
            "close": [15.0],
            "bbm_20_2": [10.0],
            "adx_14": [25.0],
        }
    )

    filters = pd.DataFrame(
        {
            "FilterCode": ["T17", "T500"],
            "PythonQuery": [
                "(relative_volume > 1.3) and (change_1w_percent < 15.0) and sma_10_keser_sma_50_yukari",
                "(change_1w_percent < 15.0) and (close > bbm_20_2) and (adx_14 > 20.0)",
            ],
        }
    )

    result, _ = filter_engine.uygula_filtreler(df, filters, pd.Timestamp("2025-03-07"))

    assert result["T17"]["sebep"] == "OK"
    assert result["T500"]["sebep"] == "OK"
