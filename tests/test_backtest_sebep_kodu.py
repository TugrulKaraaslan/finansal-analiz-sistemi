import backtest_core
import os
import sys
import pandas as pd

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


def _df():
    return pd.DataFrame(
        {
            "hisse_kodu": ["AAA", "AAA"],
            "tarih": [
                pd.to_datetime("07.03.2025", dayfirst=True),
                pd.to_datetime("10.03.2025", dayfirst=True),
            ],
            "open": [10, 12],
            "close": [11, 13],
        }
    )


def test_sebep_kodu_passthrough_ok():
    filtre = {"F1": {"hisseler": ["AAA"], "sebep": "OK", "hisse_sayisi": 1}}
    rapor_df, _ = backtest_core.calistir_basit_backtest(
        filtre, _df(), "10.03.2025", "07.03.2025"
    )
    assert rapor_df.iloc[0]["sebep_kodu"] == "OK"


def test_error_code_preserved():
    filtre = {"F1": {"hisseler": [], "sebep": "QUERY_ERROR", "hisse_sayisi": 0}}
    rapor_df, _ = backtest_core.calistir_basit_backtest(
        filtre, _df(), "10.03.2025", "07.03.2025"
    )
    assert rapor_df.iloc[0]["sebep_kodu"] == "QUERY_ERROR"
