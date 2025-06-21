import preprocessor


def test_auto_columns_generated(big_df):
    slim = big_df.drop(columns=["volume"], errors="ignore")
    out = preprocessor.on_isle_hisse_verileri(slim)
    assert {"volume_tl", "psar"}.issubset(out.columns)
