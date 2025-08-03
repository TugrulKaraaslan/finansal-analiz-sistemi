"""Validate filter CSV files and detect malformed queries.

Helper functions return reason codes so that callers can display
meaningful error messages when filter expressions fail to run.
"""

from __future__ import annotations

import logging
import re
from typing import Mapping, Optional, Sequence

import pandas as pd
from validators import ValidationError

# Acceptable characters for filter identifiers
FLAG_PATTERN: re.Pattern[str] = re.compile(r"^[A-Z0-9_\-]+$")

SEBEP_KODLARI: dict[str, str] = {
    "OK": "Filtre çalıştı ve hisse bulundu.",
    "NO_STOCK": "Sorgu sonucunda hisse bulunamadı.",
    "MISSING_COL": "Sorguda eksik sütun veya değişken.",
    "QUERY_ERROR": "Sorgu çalıştırılırken hata oluştu.",
}

__all__ = ["dogrula_filtre_dataframe", "validate", "SEBEP_KODLARI"]


def dogrula_filtre_dataframe(
    df_filtre: pd.DataFrame,
    zorunlu_kolonlar: Sequence[str] | None = None,
    logger: Optional[logging.Logger] = None,
) -> Mapping[str, str]:
    """Return problematic rows as a ``dict`` keyed by filter code.

    Args:
        df_filtre (pd.DataFrame): Filter definitions to verify.
        zorunlu_kolonlar (list[str] | None, optional): Required column names.
            Defaults to ``["flag", "query"]``.
        logger (Optional[logging.Logger], optional): Logger used for warnings.

    Returns:
        dict: Mapping of filter codes to descriptions of the issue.
    """
    issues: dict[str, str] = {}
    zorunlu_kolonlar = list(zorunlu_kolonlar or ["flag", "query"])

    eksik_kolonlar = [c for c in zorunlu_kolonlar if c not in df_filtre.columns]
    if eksik_kolonlar:
        raise KeyError("Eksik zorunlu kolonlar: " + ", ".join(eksik_kolonlar))

    flags = (
        df_filtre.get("flag", pd.Series(dtype=object))
        .fillna("")
        .astype(str)
        .str.strip()
    )
    queries = (
        df_filtre.get("query", pd.Series(dtype=object))
        .fillna("")
        .astype(str)
        .str.strip()
    )

    for idx, (flag_raw, query) in enumerate(zip(flags, queries)):
        code = flag_raw or f"satir_{idx}"
        if not flag_raw:
            issues[code] = "Boş veya eksik flag (kod) değeri."
        elif not FLAG_PATTERN.match(flag_raw):
            issues[code] = (
                "Geçersiz karakterler içeren flag. Sadece A-Z, 0-9, _ ve - izinli."
            )

        if not query:
            prefix = issues.get(code, "")
            if prefix:
                prefix = prefix.rstrip(". ") + ". "
            issues[code] = prefix + "Query sütunu boş veya eksik."

    if logger:
        for kod, mesaj in issues.items():
            logger.warning("Filtre doğrulama uyarısı (%s): %s", kod, mesaj)

    return issues


def validate(
    df_filtre: pd.DataFrame,
    zorunlu_kolonlar: Sequence[str] | None = None,
    logger: Optional[logging.Logger] = None,
) -> list[ValidationError]:
    """Return ``ValidationError`` objects describing invalid rows.

    Args:
        df_filtre (pd.DataFrame): Filter definitions to validate.
        zorunlu_kolonlar (list[str] | None, optional): Required column names.
            Defaults to ``["flag", "query"]``.
        logger (Optional[logging.Logger], optional): Logger emitting warnings for
            each problem.

    Returns:
        list[ValidationError]: Structured error objects describing validation
        failures.
    """
    zorunlu_kolonlar = list(zorunlu_kolonlar or ["flag", "query"])
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

    flags = (
        df_filtre.get("flag", pd.Series(dtype=object))
        .fillna("")
        .astype(str)
        .str.strip()
    )
    queries = (
        df_filtre.get("query", pd.Series(dtype=object))
        .fillna("")
        .astype(str)
        .str.strip()
    )

    for idx, (flag_raw, query) in enumerate(zip(flags, queries)):
        kod = flag_raw or f"satir_{idx}"

        if not flag_raw:
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
        elif not FLAG_PATTERN.match(flag_raw):
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
            logger.warning("Filtre doğrulama uyarısı (%s): %s", err.eksik_ad, err.detay)
    return errors
