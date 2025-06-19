from indicator_calculator import calculate_indicators
import os
import sys
import pandas as pd

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.modules.pop("pandas_ta", None)


def test_duplicate_columns():
    df = pd.DataFrame({"close": [1, 2, 3, 4, 5]})
    out = calculate_indicators(df.copy(), indicators=["ema_5", "ema_5"])
    assert not out.columns.duplicated().any(), "Duplicate column oluştu!"
