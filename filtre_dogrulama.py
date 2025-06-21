# filtre_dogrulama.py
# Bu modül CSV filtre dosyasındaki flag/query hatalarını tespit eder

import pandas as pd
import re

SEBEP_KODLARI = {
    "OK": "Filtre çalıştı ve hisse bulundu.",
    "NO_STOCK": "Sorgu sonucunda hisse bulunamadı.",
    "MISSING_COL": "Sorguda eksik sütun veya değişken.",
    "QUERY_ERROR": "Sorgu çalıştırılırken hata oluştu.",
}


def dogrula_filtre_dataframe(
    df_filtre: pd.DataFrame, zorunlu_kolonlar=None, logger=None
) -> dict:
    """
    Filtre DataFrame'inde flag/query eksikliği veya bozukluğu kontrol eder.
    Uygunsuz filtreleri ``{'filter_code': 'açıklama'}`` şeklinde döndürür.

    Varsayılan ``zorunlu_kolonlar`` değeri ``["flag", "query"]`` olup,
    bunlar CSV'de sırasıyla ``FilterCode`` ve ``PythonQuery`` sütunlarına
    karşılık gelir.
    """
    sorunlu = {}
    zorunlu_kolonlar = zorunlu_kolonlar or ["flag", "query"]

    eksik_kolonlar = [c for c in zorunlu_kolonlar if c not in df_filtre.columns]
    if eksik_kolonlar:
        raise KeyError("Eksik zorunlu kolonlar: " + ", ".join(eksik_kolonlar))

    for idx, row in df_filtre.iterrows():
        kod_degeri = row.get("flag")
        kod = f"satir_{idx}" if pd.isna(kod_degeri) else str(kod_degeri)
        query_degeri = row.get("query", "")
        query = "" if pd.isna(query_degeri) else str(query_degeri).strip()

        if not kod or kod.strip() == "":
            sorunlu[kod] = "Boş veya eksik flag (kod) değeri."
        elif not re.match(r"^[A-Z0-9_\-]+$", kod):
            sorunlu[
                kod
            ] = "Geçersiz karakterler içeren flag. Sadece A-Z, 0-9, _ ve - izinli."

        if "query" not in row or not query:
            sorunlu[kod] = sorunlu.get(kod, "") + " Query sütunu boş veya eksik."

    if logger:
        for kod, mesaj in sorunlu.items():
            logger.warning(f"Filtre doğrulama uyarısı ({kod}): {mesaj}")

    return sorunlu


def kod_icin_aciklama(kod: str) -> str:
    """SEBEP_KODLARI icindeki aciklamayi dondurur."""
    return SEBEP_KODLARI.get(kod, "")


# ENTEGRASYON (data_loader.py içinde):
# from filtre_dogrulama import dogrula_filtre_dataframe
# ...
# df_filtreler = pd.read_csv(filtre_dosya_yolu, ...)
# hatalar = dogrula_filtre_dataframe(df_filtreler, logger=logger)
# if hatalar:
#     for kod, mesaj in hatalar.items():
#         logger.warning(f"Hatalı filtre: {kod} - {mesaj}")
