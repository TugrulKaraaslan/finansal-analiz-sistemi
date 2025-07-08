import pandas as pd

import preprocessor


def test_volume_tl_auto_added():
    """Test test_volume_tl_auto_added."""
    df = pd.DataFrame(
        {
            "hisse_kodu": ["AAA"],
            "tarih": [pd.Timestamp("2025-03-01")],
            "open": [1.0],
            "high": [1.0],
            "low": [1.0],
            "close": [2.0],
            "volume": [5.0],
        }
    )
    processed = preprocessor.on_isle_hisse_verileri(df)
    assert "volume_tl" in processed.columns
    assert processed.loc[0, "volume_tl"] == 10.0
