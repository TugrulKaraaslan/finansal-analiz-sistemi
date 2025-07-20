"""Lightweight data preprocessing helpers.

These functions normalize numeric columns, adjust date fields and drop
invalid rows before indicator calculation.
"""

from __future__ import annotations

import logging
import re
from typing import Optional

import numpy as np
import pandas as pd
from pandas import CategoricalDtype

from finansal_analiz_sistemi import config
from finansal_analiz_sistemi.logging_config import get_logger

logger = get_logger(__name__)

try:
    import holidays

    logger.debug("Python 'holidays' kütüphanesi başarıyla import edildi.")
except ImportError:
    holidays = None
    logger.warning(
        "Python 'holidays' kütüphanesi bulunamadı. Tatil günü filtrelemesi yapılamayacak."
    )


# Regex and translation table used to normalize numeric strings
_NUMERIC_RE = re.compile(r"[^\d,.-]+")
_TRANSLATE = str.maketrans({".": "", ",": "."})


def _temizle_sayisal_deger(deger: object) -> float:
    """Return ``deger`` converted to ``float`` when possible.

    Strings may use Turkish number formatting. Thousands separators are
    removed and decimal commas are replaced with dots. Unsupported values
    produce ``np.nan``.
    """

    if pd.isna(deger):
        return np.nan

    if isinstance(deger, (int, float, np.number)):
        return float(deger)

    if isinstance(deger, str):
        cleaned = _NUMERIC_RE.sub("", deger.strip())
        cleaned = cleaned.translate(_TRANSLATE)
        try:
            return float(cleaned)
        except ValueError:
            return np.nan

    return np.nan


def _temizle_sayisal_seri(s: pd.Series) -> pd.Series:
    """Vectorized variant of :func:`_temizle_sayisal_deger`."""
    if pd.api.types.is_numeric_dtype(s):
        return s.astype(float)
    cleaned = s.astype(str).str.replace(_NUMERIC_RE, "", regex=True)
    cleaned = cleaned.str.translate(_TRANSLATE)
    return pd.to_numeric(cleaned, errors="coerce").astype(float)


def _convert_numeric_columns(
    df: pd.DataFrame, columns: list[str], logger_param: Optional[logging.Logger] = None
) -> None:
    """Ensure ``columns`` in ``df`` are numeric.

    Non-numeric values are coerced to ``float`` and missing required columns
    emit a warning via the provided logger.

    Parameters
    ----------
    df : pandas.DataFrame
        Frame to modify in place.
    columns : list[str]
        Column names expected to hold numeric values.
    logger_param : Optional[logging.Logger], optional
        Logger used for warnings. Defaults to module logger.
    """
    if logger_param is None:
        logger_param = logger

    for col in columns:
        if col not in df.columns:
            if col in ["open", "high", "low", "close", "volume"]:
                logger_param.warning(
                    "Ön işleme için beklenen temel sütun '%s' DataFrame'de bulunamadı.",
                    col,
                )
            continue

        series = df[col]
        col_dtype = series.dtype

        if pd.api.types.is_numeric_dtype(col_dtype):
            if col_dtype != float:
                df[col] = series.astype(float, errors="ignore")
            continue

        if pd.api.types.is_object_dtype(col_dtype) or isinstance(
            col_dtype, CategoricalDtype
        ):
            nan_before = series.isnull().sum()
            df[col] = _temizle_sayisal_seri(series)
            nan_after = df[col].isnull().sum()
            if nan_after > nan_before:
                logger_param.warning(
                    "'%s' (orijinal tip: %s) sütununda sayısal dönüşüm sonrası NaN sayısı arttı (%s -> %s).",
                    col,
                    col_dtype,
                    nan_before,
                    nan_after,
                )
            continue

        logger_param.warning(
            "Column '%s' has unexpected type (%s); attempting float conversion.",
            col,
            col_dtype,
        )
        df[col] = pd.to_numeric(series, errors="coerce")


def on_isle_hisse_verileri(
    df_ham: pd.DataFrame, logger_param: Optional[logging.Logger] = None
) -> pd.DataFrame | None:
    """Clean raw stock data for indicator calculation.

    The step converts date fields, normalizes numeric columns, drops invalid
    rows and optionally filters out BIST holidays.
    """
    if logger_param is None:
        logger_param = logger
    fn_logger = logger_param
    fn_logger.info("Veri ön işleme adımı başlatılıyor...")

    if df_ham is None or df_ham.empty:
        fn_logger.error(
            "Ön işleme için ham veri (df_ham) boş veya None. İşlem durduruluyor."
        )
        return None

    df = df_ham.copy()
    fn_logger.debug(f"Ön işleme başlangıç satır sayısı: {len(df)}")

    # Validate and convert the date column
    if "tarih" not in df.columns:
        fn_logger.critical(
            "'tarih' sütunu DataFrame'de bulunamadı. Ön işleme devam edemez."
        )
        return None  # Critical missing column, abort processing.

    if not pd.api.types.is_datetime64_any_dtype(df["tarih"]):
        fn_logger.warning(
            "'tarih' sütunu henüz datetime formatında değil, dönüştürülüyor (preprocessor)..."
        )
        try:
            # Use common formats; invalid dates become NaT
            df["tarih"] = pd.to_datetime(df["tarih"], errors="coerce", dayfirst=True)
            fn_logger.info(
                "'tarih' sütunu preprocessor'da başarıyla datetime formatına dönüştürüldü."
            )
        except Exception as e_date_conv:
            fn_logger.error(
                f"'tarih' sütunu preprocessor'da da datetime'a dönüştürülemedi: {e_date_conv}. "
                "Hatalı değerler NaT olacak.",
                exc_info=True,
            )
            # NaT rows are removed later

    nat_count_initial = df["tarih"].isnull().sum()
    if nat_count_initial > 0:
        fn_logger.warning(
            f"After conversion {nat_count_initial} NaT (Not a Time) values were found in the 'tarih' column."
        )
    df.dropna(subset=["tarih"], inplace=True)  # Drop rows without valid dates
    rows_dropped_for_nat = nat_count_initial - df["tarih"].isnull().sum()
    if rows_dropped_for_nat > 0:
        fn_logger.info(
            f"Dropped {rows_dropped_for_nat} rows due to NaT values in the 'tarih' column."
        )
    if df.empty:
        fn_logger.error(
            "All entries in the 'tarih' column were NaT. Preprocessing aborted."
        )
        return None

    # 2. Convert OHLCV and volume columns to numeric types
    # Expected numeric after data loader
    sayisal_hedef_sutunlar = ["open", "high", "low", "close", "volume"]
    if (
        "adj_close" in df.columns and "adj_close" not in sayisal_hedef_sutunlar
    ):  # Include adj_close when present
        sayisal_hedef_sutunlar.append("adj_close")
    if (
        "volume_tl" in df.columns and "volume_tl" not in sayisal_hedef_sutunlar
    ):  # Include volume_tl when available (should be numeric)
        sayisal_hedef_sutunlar.append("volume_tl")

    _convert_numeric_columns(df, sayisal_hedef_sutunlar, fn_logger)
    fn_logger.info(
        "OHLCV ve volume sütunları sayısal tipe dönüştürüldü/kontrol edildi."
    )

    # Otomatik türetilen kolonlar
    if {
        "volume",
        "close",
    } <= set(df.columns) and "volume_tl" not in df.columns:
        df["volume_tl"] = df["volume"] * df["close"]
        fn_logger.debug("'volume_tl' sütunu otomatik eklendi.")
    if {
        "psar_long",
        "psar_short",
    } <= set(df.columns) and "psar" not in df.columns:
        df["psar"] = df["psar_long"].fillna(df["psar_short"])
        fn_logger.debug("'psar' sütunu otomatik eklendi.")
    if {
        "volume",
        "close",
    } <= set(df.columns) and "volume_price" not in df.columns:
        df["volume_price"] = df["volume"] * df["close"]
        fn_logger.debug("'volume_price' sütunu otomatik eklendi.")
    if {
        "open",
        "close",
    } <= set(df.columns) and "change_from_open_percent" not in df.columns:
        df["change_from_open_percent"] = (df["close"] - df["open"]) / df["open"] * 100
        fn_logger.debug("'change_from_open_percent' sütunu otomatik eklendi.")

    # 3. Drop rows with NaN values in critical OHLC columns
    kritik_ohlc_sutunlar = [
        "open",
        "high",
        "low",
        "close",
    ]  # 'volume' NaN values can be filled with zero
    eksik_kritik_sutunlar = [s for s in kritik_ohlc_sutunlar if s not in df.columns]
    if eksik_kritik_sutunlar:
        fn_logger.error(
            f"Kritik OHLC sütunlarından bazıları yükleme/standardizasyon sonrası hala eksik: "
            f"{eksik_kritik_sutunlar}. NaN temizliği bu sütunlar olmadan yapılamaz."
        )
        # Stop entirely if all core OHLC columns are missing
        if len(eksik_kritik_sutunlar) == len(kritik_ohlc_sutunlar):  # Hepsi eksikse
            fn_logger.critical(
                "Tüm kritik OHLC sütunları eksik. Ön işleme durduruluyor."
            )
            return None
    else:
        nan_oncesi_satir_sayisi = len(df)
        df.dropna(subset=kritik_ohlc_sutunlar, inplace=True)
        rows_dropped_for_ohlc_nan = nan_oncesi_satir_sayisi - len(df)
        if rows_dropped_for_ohlc_nan > 0:
            fn_logger.info(
                f"Kritik OHLC sütunlarındaki (en az birinde) NaN değerler nedeniyle "
                f"{rows_dropped_for_ohlc_nan} satır çıkarıldı."
            )

    # 4. Fill NaN values in volume with zero (optional per strategy)
    if "volume" in df.columns and df["volume"].isnull().any():
        nan_count_volume_before_fill = df["volume"].isnull().sum()
        df["volume"].fillna(0, inplace=True)
        fn_logger.info(
            f"'volume' sütunundaki {nan_count_volume_before_fill} adet NaN değer 0 ile dolduruldu."
        )

    if df.empty:
        fn_logger.error(
            "Kritik veri temizliği (tarih, OHLC NaN'ları) sonrası DataFrame boş kaldı. Ön işleme durduruluyor."
        )
        return None
    fn_logger.info("Kritik NaN değer yönetimi tamamlandı.")

    # 5. Sort data by ticker code and date
    if "hisse_kodu" not in df.columns:
        fn_logger.critical(
            "'hisse_kodu' sütunu DataFrame'de bulunamadı. Sıralama yapılamıyor. Ön işleme durduruluyor."
        )
        return None

    df.sort_values(by=["hisse_kodu", "tarih"], ascending=[True, True], inplace=True)
    df.reset_index(drop=True, inplace=True)  # Create a clean sequential index
    fn_logger.info("Veri 'hisse_kodu' ve 'tarih'e göre sıralandı, index sıfırlandı.")

    # 6. Remove BIST holidays (optional)
    if holidays and config.TR_HOLIDAYS_REMOVE:
        try:
            unique_years = df["tarih"].dt.year.unique()
            if (
                len(unique_years) > 0 and pd.notna(unique_years).all()
            ):  # Proceed only when the year values are valid
                tr_holidays = holidays.Turkey(years=unique_years)
                # Normalize to date-only before comparison
                original_len = len(df)
                normalized_dates = pd.to_datetime(df["tarih"].dt.normalize())
                holiday_dates = pd.to_datetime(list(tr_holidays.keys()))
                df = df[~normalized_dates.isin(holiday_dates)]
                rows_dropped_for_holidays = original_len - len(df)
                if rows_dropped_for_holidays > 0:
                    fn_logger.info(
                        f"BIST resmi tatil günleri nedeniyle {rows_dropped_for_holidays} satır çıkarıldı."
                    )
                else:
                    fn_logger.info(
                        "BIST resmi tatil günleri kontrol edildi, çıkarılacak ek satır bulunamadı."
                    )
            else:
                fn_logger.info(
                    "Veride geçerli yıl bulunamadığı veya NaN yıllar olduğu için tatil günü çıkarma işlemi atlandı."
                )
        except Exception as e_holiday:
            fn_logger.warning(
                f"Tatil günleri çıkarılırken bir hata oluştu: {e_holiday}. Bu adım atlanıyor.",
                exc_info=False,
            )

    fn_logger.info(f"Ön işleme tamamlandı. Son satır sayısı: {len(df)}")
    if not df.empty:
        fn_logger.debug(
            f"İşlenmiş veri örneği (ilk 3 satır):\n{df.head(3).to_string()}"
        )
    else:
        fn_logger.warning("Ön işleme sonucu DataFrame boş.")

    return df
