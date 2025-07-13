"""Validate filter CSV files and flag malformed queries.

The helpers return reason codes so callers can surface meaningful error
messages when filters cannot be executed.
"""

import re

import pandas as pd

from validators import ValidationError

SEBEP_KODLARI = {
    "OK": "Filtre çalıştı ve hisse bulundu.",
    "NO_STOCK": "Sorgu sonucunda hisse bulunamadı.",
    "MISSING_COL": "Sorguda eksik sütun veya değişken.",
    "QUERY_ERROR": "Sorgu çalıştırılırken hata oluştu.",
}


def dogrula_filtre_dataframe(
    df_filtre: pd.DataFrame, zorunlu_kolonlar=None, logger=None
) -> dict:
    """Validate a filter DataFrame and map invalid rows to a reason.

    Args:
        df_filtre (pd.DataFrame): Filter definitions to verify.
        zorunlu_kolonlar (list[str] | None, optional): Columns expected in
            ``df_filtre``. Defaults to ``["flag", "query"]``.
        logger (optional): Logger instance for warning messages.

    Returns:
        dict: Mapping of ``filter_code`` to a short description when the row
        is invalid.

    """
    sorunlu = {}
    zorunlu_kolonlar = zorunlu_kolonlar or ["flag", "query"]

    eksik_kolonlar = [c for c in zorunlu_kolonlar if c not in df_filtre.columns]
    if eksik_kolonlar:
        raise KeyError("Eksik zorunlu kolonlar: " + ", ".join(eksik_kolonlar))

    for idx, row in df_filtre.iterrows():
        kod_degeri = row.get("flag")
        kod_raw = "" if pd.isna(kod_degeri) else str(kod_degeri).strip()
        kod = kod_raw or f"satir_{idx}"
        query_degeri = row.get("query", "")
        query = "" if pd.isna(query_degeri) else str(query_degeri).strip()

        if not kod_raw:
            sorunlu[kod] = "Boş veya eksik flag (kod) değeri."
        elif not re.match(r"^[A-Z0-9_\-]+$", kod_raw):
            sorunlu[kod] = (
                "Geçersiz karakterler içeren flag. Sadece A-Z, 0-9, _ ve - izinli."
            )

        if "query" not in row or not query:
            prefix = sorunlu.get(kod, "")
            if prefix:
                prefix = prefix.rstrip(". ") + ". "
            sorunlu[kod] = prefix + "Query sütunu boş veya eksik."

    if logger:
        for kod, mesaj in sorunlu.items():
            logger.warning(f"Filtre doğrulama uyarısı ({kod}): {mesaj}")

    return sorunlu


def validate(
    df_filtre: pd.DataFrame, zorunlu_kolonlar=None, logger=None
) -> list[ValidationError]:
    """Return ``ValidationError`` objects for each invalid filter row.

    Args:
        df_filtre (pd.DataFrame): Filter definitions to validate.
        zorunlu_kolonlar (list[str] | None, optional): Required column names,
            defaults to ``["flag", "query"]``.
        logger (optional): Logger for warnings.

    Returns:
        list[ValidationError]: Structured error objects describing validation
        failures.

    """
    zorunlu_kolonlar = zorunlu_kolonlar or ["flag", "query"]
    errors: list[ValidationError] = []

    eksik = [c for c in zorunlu_kolonlar if c not in df_filtre.columns]
    if eksik:
        errors.append(
            ValidationError(
                hata_tipi="MISSING_COL",
                eksik_ad=",".join(eksik),
                detay=f"Eksik zorunlu kolonlar: {', '.join(eksik)}",
                cozum_onerisi="CSV başlıklarını kontrol edin",
                reason="missing_column",
                hint="flag ve query sütunları gereklidir",
            )
        )
        return errors

    for idx, row in df_filtre.iterrows():
        kod_degeri = row.get("flag")
        kod_raw = "" if pd.isna(kod_degeri) else str(kod_degeri).strip()
        kod = kod_raw or f"satir_{idx}"
        query_degeri = row.get("query", "")
        query = "" if pd.isna(query_degeri) else str(query_degeri).strip()

        if not kod_raw:
            errors.append(
                ValidationError(
                    hata_tipi="MISSING_FLAG",
                    eksik_ad="flag",
                    detay=f"Boş veya eksik flag (kod) değeri: satır {idx}",
                    cozum_onerisi="flag kolonunu doldurun",
                    reason="missing_flag",
                    hint="Her filtre için bir kod girilmeli",
                )
            )
        elif not re.match(r"^[A-Z0-9_\-]+$", kod_raw):
            errors.append(
                ValidationError(
                    hata_tipi="INVALID_FLAG",
                    eksik_ad=kod,
                    detay="Geçersiz karakterler içeren flag",
                    cozum_onerisi="Sadece A-Z, 0-9, _ ve - kullanın",
                    reason="invalid_flag",
                    hint="Kodlar A-Z0-9_- ile sınırlıdır",
                )
            )

        if not query:
            errors.append(
                ValidationError(
                    hata_tipi="MISSING_QUERY",
                    eksik_ad=kod,
                    detay="Query sütunu boş veya eksik",
                    cozum_onerisi="PythonQuery alanını doldurun",
                    reason="missing_query",
                    hint="Sorgu satırı boş bırakılmamalı",
                )
            )

    if logger:
        for err in errors:
            logger.warning(f"Filtre doğrulama uyarısı ({err.eksik_ad}): {err.detay}")
    return errors
