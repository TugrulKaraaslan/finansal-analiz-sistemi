"""Data preprocessing helpers for stock price datasets.

Utilities here clean numeric values and align dates before indicators
are computed.
"""

from __future__ import annotations

import re

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


def _temizle_sayisal_deger(deger):
    """Return ``deger`` as ``float`` if it can be parsed.

    Strings are stripped of non-numeric characters and Turkish style
    thousand/decimal separators are normalized. ``np.nan`` is returned when
    conversion fails.
    """
    if pd.isna(deger):
        return np.nan
    if isinstance(
        deger, (int, float, np.number)
    ):  # np.number, numpy'nin sayısal tiplerini de kapsar
        return float(deger)
    if isinstance(deger, str):
        # Sadece rakam, virgül, nokta ve eksi işaretini tut, diğerlerini temizle
        temizlenmis_deger = re.sub(r"[^\d,.-]+", "", deger.strip())
        # Türkçe sayı formatı (binlik ayıracı nokta, ondalık ayıracı virgül) ise:
        # Önce tüm binlik ayraçlarını (noktaları) kaldır
        temizlenmis_deger_noktasiz = temizlenmis_deger.replace(".", "")
        # Sonra ondalık ayıracını (virgülü) noktaya çevir
        temizlenmis_deger_standart = temizlenmis_deger_noktasiz.replace(",", ".")

        # Eğer ilk denemede (noktasız, virgül->nokta) float'a dönüşürse kullan
        try:
            return float(temizlenmis_deger_standart)
        except ValueError:
            # Eğer yukarıdaki başarısız olursa, orijinal temizlenmiş değeri (belki
            # zaten standart 1.234,56 değil de 1234.56 formatındadır) dene
            try:
                return float(
                    temizlenmis_deger
                )  # Orijinal string'den sadece sayısal olmayanları attık
            except ValueError:
                return np.nan
    return np.nan  # Diğer tüm beklenmedik tipler için


def on_isle_hisse_verileri(
    df_ham: pd.DataFrame, logger_param=None
) -> pd.DataFrame | None:
    """Preprocess raw equity data.

    - Fix date format and handle ``NaT`` values.
    - Convert OHLCV and volume columns to numeric.
    - Manage NaN values in critical columns.
    - Sort the dataset.
    - Optionally remove BIST holidays.
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

    # 1. Tarih Sütunu Kontrolü ve Dönüşümü
    # data_loader'da 'tarih' sütununun varlığı ve temel standardizasyonu yapıldı.
    # Burada datetime tipinde olduğundan emin olalım ve NaT'leri yönetelim.
    if "tarih" not in df.columns:
        fn_logger.critical(
            "'tarih' sütunu DataFrame'de bulunamadı. Ön işleme devam edemez."
        )
        return None  # Kritik eksiklik, devam etmek anlamsız.

    if not pd.api.types.is_datetime64_any_dtype(df["tarih"]):
        fn_logger.warning(
            "'tarih' sütunu henüz datetime formatında değil, dönüştürülüyor (preprocessor)..."
        )
        try:
            # Olası farklı formatları dene (genellikle pd.to_datetime bunu otomatik
            # yapar ama garanti olsun)
            df["tarih"] = pd.to_datetime(df["tarih"], errors="coerce", dayfirst=True)
            # errors='coerce' geçersiz tarihleri NaT (Not a Time) yapar.
            # dayfirst=True, dd.mm.yyyy formatını önceliklendirir.
            fn_logger.info(
                "'tarih' sütunu preprocessor'da başarıyla datetime formatına dönüştürüldü."
            )
        except Exception as e_date_conv:
            fn_logger.error(
                f"'tarih' sütunu preprocessor'da da datetime'a dönüştürülemedi: {e_date_conv}. "
                "Hatalı değerler NaT olacak.",
                exc_info=True,
            )
            # Hata durumunda bile devam et, NaT olanlar aşağıda drop edilecek.

    nat_count_initial = df["tarih"].isnull().sum()
    if nat_count_initial > 0:
        fn_logger.warning(
            f"Dönüşüm sonrası 'tarih' sütununda {nat_count_initial} adet NaT (Not a Time) değer bulundu."
        )
    df.dropna(
        subset=["tarih"], inplace=True
    )  # Tarih bilgisi olmayan (NaT) satırları çıkar
    rows_dropped_for_nat = nat_count_initial - df["tarih"].isnull().sum()
    if rows_dropped_for_nat > 0:
        fn_logger.info(
            f"Tarih sütunundaki NaT değerler nedeniyle {rows_dropped_for_nat} satır çıkarıldı."
        )
    if df.empty:
        fn_logger.error(
            "Tarih sütunundaki tüm değerler NaT olduğu için DataFrame boş kaldı. Ön işleme durduruluyor."
        )
        return None

    # 2. OHLCV ve Volume Sütunlarını Sayısal Tipe Dönüştürme
    # data_loader bu sütunları 'open', 'high', 'low', 'close', 'volume' olarak
    # standartlaştırdı.
    sayisal_hedef_sutunlar = ["open", "high", "low", "close", "volume"]
    if (
        "adj_close" in df.columns and "adj_close" not in sayisal_hedef_sutunlar
    ):  # Eğer varsa adj_close'u da dahil et
        sayisal_hedef_sutunlar.append("adj_close")
    if (
        "volume_tl" in df.columns and "volume_tl" not in sayisal_hedef_sutunlar
    ):  # Eğer varsa volume_tl'yi de dahil et (sayısal olmalı)
        sayisal_hedef_sutunlar.append("volume_tl")

    for col in sayisal_hedef_sutunlar:
        if col in df.columns:
            # Eğer sütun object (string) tipindeyse veya kategorikse, sayısal yapmaya
            # çalış
            if df[col].dtype == "object" or isinstance(df[col].dtype, CategoricalDtype):
                nan_before = df[col].isnull().sum()
                original_type = df[col].dtype
                df[col] = (
                    df[col].apply(_temizle_sayisal_deger).astype(float)
                )  # _temizle_sayisal_deger NaN veya float döner
                nan_after = df[col].isnull().sum()
                if nan_after > nan_before:
                    fn_logger.warning(
                        f"'{col}' (orijinal tip: {original_type}) sütununda sayısal dönüşüm sonrası NaN sayısı arttı "
                        f"({nan_before} -> {nan_after})."
                    )
            elif not pd.api.types.is_numeric_dtype(
                df[col]
            ):  # Sayısal değilse ama object de değilse (örn: boolean?)
                fn_logger.warning(
                    f"'{col}' sütunu beklenmedik bir tipte ({df[col].dtype}), float'a dönüştürülmeye çalışılıyor."
                )
                df[col] = pd.to_numeric(
                    df[col], errors="coerce"
                )  # Hataları NaT/NaN yapar
            # Eğer zaten sayısal bir tipse ve float değilse, float'a çevir
            elif df[col].dtype != float:
                # errors='ignore' sorunlu dönüşümlerde orijinal değeri korur (nadiren
                # olmalı)
                df[col] = df[col].astype(float, errors="ignore")
        else:
            # Bu uyarı data_loader'da daha detaylı verildi, burada tekrar etmeye gerek yok.
            # Sadece ana OHLCV için bir son kontrol yapılabilir.
            if col in ["open", "high", "low", "close", "volume"]:
                fn_logger.warning(
                    f"Ön işleme için beklenen temel sütun '{col}' DataFrame'de bulunamadı."
                )
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

    # 3. Kritik OHLC Sütunlarında NaN Varsa Satırları Çıkar
    kritik_ohlc_sutunlar = [
        "open",
        "high",
        "low",
        "close",
    ]  # 'volume' NaN'ları 0 ile doldurulabilir.
    eksik_kritik_sutunlar = [s for s in kritik_ohlc_sutunlar if s not in df.columns]
    if eksik_kritik_sutunlar:
        fn_logger.error(
            f"Kritik OHLC sütunlarından bazıları yükleme/standardizasyon sonrası hala eksik: "
            f"{eksik_kritik_sutunlar}. NaN temizliği bu sütunlar olmadan yapılamaz."
        )
        # Eğer temel OHLC eksikse, devam etmek anlamsız olabilir.
        if len(eksik_kritik_sutunlar) == len(kritik_ohlc_sutunlar):  # Hepsi eksikse
            fn_logger.critical(
                "Tüm kritik OHLC sütunları eksik. Ön işleme durduruluyor."
            )
            return None
    else:
        nan_oncesi_satir_sayisi = len(df)
        df.dropna(
            subset=kritik_ohlc_sutunlar, inplace=True
        )  # how='any' (varsayılan): Herhangi birinde NaN varsa satırı çıkar
        rows_dropped_for_ohlc_nan = nan_oncesi_satir_sayisi - len(df)
        if rows_dropped_for_ohlc_nan > 0:
            fn_logger.info(
                f"Kritik OHLC sütunlarındaki (en az birinde) NaN değerler nedeniyle "
                f"{rows_dropped_for_ohlc_nan} satır çıkarıldı."
            )

    # 4. Hacimdeki NaN'ları 0 İle Doldur (Opsiyonel, stratejiye göre değişebilir)
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

    # 5. Veriyi Hisse Kodu ve Tarihe Göre Sırala
    if "hisse_kodu" not in df.columns:
        fn_logger.critical(
            "'hisse_kodu' sütunu DataFrame'de bulunamadı. Sıralama yapılamıyor. Ön işleme durduruluyor."
        )
        return None

    df.sort_values(by=["hisse_kodu", "tarih"], ascending=[True, True], inplace=True)
    df.reset_index(drop=True, inplace=True)  # Temiz bir sıralı indeks oluştur
    fn_logger.info("Veri 'hisse_kodu' ve 'tarih'e göre sıralandı, index sıfırlandı.")

    # 6. BIST Tatil Günlerini Çıkar (Opsiyonel)
    if holidays and config.TR_HOLIDAYS_REMOVE:
        try:
            unique_years = df["tarih"].dt.year.unique()
            if (
                len(unique_years) > 0 and pd.notna(unique_years).all()
            ):  # Geçerli yıllar varsa
                tr_holidays = holidays.Turkey(years=unique_years)
                # Tarihleri karşılaştırmadan önce normalize et (sadece tarih kısmı, saat
                # bilgisi olmadan)
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
