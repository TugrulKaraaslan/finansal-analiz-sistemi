import preprocessor
import pandas as pd


def test_auto_columns_generated(big_df):
    slim = big_df.head(1000).copy()
    slim["psar_long"] = slim["high"]
    slim["psar_short"] = slim["low"]
    out = preprocessor.on_isle_hisse_verileri(slim)
    assert {"volume_tl", "psar"}.issubset(out.columns)
