import pandas as pd
from filter_engine import _apply_single_filter


def tarama_denetimi(df_filtreler: pd.DataFrame, df_indikator: pd.DataFrame) -> pd.DataFrame:
    """Her filtre satırını çalıştırıp _apply_single_filter'in info sözlüğünü
    toplar.

    Çıktı kolonları:
        ["kod", "tip", "durum", "sebep",
         "eksik_sutunlar", "nan_sutunlar", "secim_adedi"]
    """
    kayıtlar = []
    for _, sat in df_filtreler.iterrows():
        _, info = _apply_single_filter(df_indikator, sat["kod"], sat["PythonQuery"])
        kayıtlar.append(info)
    return pd.DataFrame(kayıtlar)
