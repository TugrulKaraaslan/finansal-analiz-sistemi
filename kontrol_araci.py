"""Filtre sonuçlarını özetleyen yardımcı fonksiyon."""

import pandas as pd

from filter_engine import _apply_single_filter


def tarama_denetimi(
    df_filtreler: pd.DataFrame, df_indikator: pd.DataFrame
) -> pd.DataFrame:
    """Tüm filtreleri tek tek çalıştırıp ``_apply_single_filter`` bilgisini toplar.

    ``df_filtreler`` eskiden ``FilterCode`` isimli bir sütun içeriyordu. Geriye
    dönük uyumluluk amacıyla bu sütun tespit edilirse ``kod`` alanına
    dönüştürülür. Sonuç satırlarında herhangi bir hata bulunmazsa fonksiyonun
    çıktısına ek olarak bir ``_SUMMARY`` satırı eklenir.
    """

    if "kod" not in df_filtreler.columns and "FilterCode" in df_filtreler.columns:
        df_filtreler = df_filtreler.rename(columns={"FilterCode": "kod"})

    kayitlar: list[dict] = []
    for _, sat in df_filtreler.iterrows():
        _, info = _apply_single_filter(df_indikator, sat["kod"], sat["PythonQuery"])
        kayitlar.append(info)

    df = pd.DataFrame(kayitlar)
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
