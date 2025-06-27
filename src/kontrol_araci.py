import pandas as pd

try:
    from .filter_engine import _apply_single_filter
except ImportError:  # pragma: no cover - fallback when run as script
    from filter_engine import _apply_single_filter


def tarama_denetimi(
    df_filtreler: pd.DataFrame, df_indikator: pd.DataFrame
) -> pd.DataFrame:
    """Her filtre satırını çalıştırıp _apply_single_filter'in info sözlüğünü
    toplar.

    Çıktı kolonları:
        ["kod", "tip", "durum", "sebep",
         "eksik_sutunlar", "nan_sutunlar", "secim_adedi"]
    """
    # --- HOT-PATCH C2: kolon uyum katmanı -----------------
    if "kod" not in df_filtreler.columns and "FilterCode" in df_filtreler.columns:
        df_filtreler = df_filtreler.rename(columns={"FilterCode": "kod"})
    # ------------------------------------------------------
    kayıtlar = []
    for _, sat in df_filtreler.iterrows():
        _, info = _apply_single_filter(df_indikator, sat["kod"], sat["PythonQuery"])
        kayıtlar.append(info)
    df = pd.DataFrame(kayıtlar)
    if not (df["durum"] != "OK").any():
        df = pd.concat(
            [
                df,
                pd.DataFrame(
                    [
                        {
                            "kod": "_SUMMARY",
                            "tip": "tarama",
                            "durum": "NO_ISSUE",
                            "sebep": "",
                            "eksik_sutunlar": "",
                            "nan_sutunlar": "",
                            "secim_adedi": 0,
                        }
                    ]
                ),
            ],
            ignore_index=True,
        )
    return df
