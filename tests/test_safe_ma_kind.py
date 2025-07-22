import pandas as pd

import indicator_calculator as ic


def test_safe_ma_unknown_kind(caplog):
    df = pd.DataFrame({"close": [1, 2, 3, 4]})
    with caplog.at_level("ERROR"):
        ic.safe_ma(df, 5, "xyz")
    assert "xyz_5" not in df.columns
    assert any("bilinmeyen" in rec.message for rec in caplog.records)
