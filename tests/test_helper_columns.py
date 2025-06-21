import preprocessor


def test_auto_columns_generated(big_df):
    out = preprocessor.on_isle_hisse_verileri(big_df)
    assert "volume_tl" in out.columns
