# filtre_dogrulama.py
# Bu modül CSV filtre dosyasındaki flag/query hatalarını tespit eder

import pandas as pd
import re

def dogrula_filtre_dataframe(df_filtre: pd.DataFrame, zorunlu_kolonlar=None, logger=None) -> dict:
    """
    Filtre DataFrame'inde flag/query eksikliği veya bozukluğu kontrol eder.
    Uygunsuz filtreleri ``{'filter_code': 'açıklama'}`` şeklinde döndürür.

    Varsayılan ``zorunlu_kolonlar`` değeri ``["flag", "query"]`` olup,
    bunlar CSV'de sırasıyla ``FilterCode`` ve ``PythonQuery`` sütunlarına
    karşılık gelir.
    """
    sorunlu = {}
    zorunlu_kolonlar = zorunlu_kolonlar or ["flag", "query"]

    for idx, row in df_filtre.iterrows():
        kod = row.get("flag") or f"satir_{idx}"
        query = str(row.get("query", "")).strip()

        if not kod or kod.strip() == "":
            sorunlu[kod] = "Boş veya eksik flag (kod) değeri."
        elif not re.match(r"^[A-Z0-9_\-]+$", kod):
            sorunlu[kod] = "Geçersiz karakterler içeren flag. Sadece A-Z, 0-9, _ ve - izinli."

        if "query" not in row or not query:
            sorunlu[kod] = sorunlu.get(kod, "") + " Query sütunu boş veya eksik."

    if logger:
        for kod, mesaj in sorunlu.items():
            logger.warning(f"Filtre doğrulama uyarısı ({kod}): {mesaj}")

    return sorunlu

# ENTEGRASYON (data_loader.py içinde):
# from filtre_dogrulama import dogrula_filtre_dataframe
# ...
# df_filtreler = pd.read_csv(filtre_dosya_yolu, ...)
# hatalar = dogrula_filtre_dataframe(df_filtreler, logger=logger)
# if hatalar:
#     for kod, mesaj in hatalar.items():
#         logger.warning(f"Hatalı filtre: {kod} - {mesaj}")
