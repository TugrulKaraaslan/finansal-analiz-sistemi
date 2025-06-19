import pandas as pd
from filter_engine import _apply_single_filter


def tarama_denetimi(
    df_filtreler: pd.DataFrame, df_indikator: pd.DataFrame
) -> pd.DataFrame:
    """Tüm filtreleri tek tek çalıştırıp _apply_single_filter çıktısını toplar."""
    kayitlar = []
    for _, sat in df_filtreler.iterrows():
        _, info = _apply_single_filter(
            df_indikator,
            sat["kod"],
            sat["PythonQuery"],
        )
        kayitlar.append(info)
    return pd.DataFrame(kayitlar)
