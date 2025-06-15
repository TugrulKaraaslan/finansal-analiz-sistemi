import os
import sys
import pandas as pd

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import filter_engine


def test_no_stock_reason_for_empty_result():
    df = pd.DataFrame({
        "hisse_kodu": ["AAA"],
        "tarih": [pd.Timestamp("2025-03-01")],
        "close": [10],
    })
    filters = pd.DataFrame({"FilterCode": ["F1"], "PythonQuery": ["close > 100"]})

    result, _ = filter_engine.uygula_filtreler(
        df, filters, pd.Timestamp("2025-03-01")
    )
    assert result["F1"]["sebep"] == "NO_STOCK"
    assert result["F1"]["hisse_sayisi"] == 0

