# data_loader.py
# -*- coding: utf-8 -*-
# Proje: Finansal Analiz ve Backtest Sistemi Geliştirme
# Modül: Veri Yükleme (Excel/CSV/Parquet) ve Filtre Dosyası Okuma
# Tuğrul Karaaslan & Gemini
# Tarih: 18 Mayıs 2025 (OHLCV_MAP kullanımı ve loglama detaylandırıldı)

import pandas as pd
import os
import glob
import config
from functools import lru_cache, partial

from data_loader_cache import DataLoaderCache

try:
    from logger_setup import get_logger

    logger = get_logger(__name__)
except ImportError:
    import logging

    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    logger = logging.getLogger(__name__)

_cache_loader = DataLoaderCache(logger=logger)


_read_excel = partial(pd.read_excel, engine="openpyxl")


@lru_cache(maxsize=None)
def _read_excel_cached(path: str) -> pd.DataFrame:
    """Read Excel files with LRU caching."""
    return _read_excel(path)


def check_and_create_dirs(*dir_paths):
    for dir_path in dir_paths:
        if dir_path and not os.path.exists(dir_path):
            try:
                os.makedirs(dir_path, exist_ok=True)
                logger.info(f"Dizin oluşturuldu: {dir_path}")
            except Exception as e:
                logger.error(
                    f"Dizin oluşturulamadı: {dir_path}. Hata: {e}", exc_info=True
                )


def load_excel_katalogu(path: str, logger_param=None) -> pd.DataFrame | None:
    """Load an Excel file and cache the result, writing Parquet if needed."""
    log = logger_param or logger
    try:
        df = _read_excel_cached(path)
    except Exception as e:
        log.error(f"Excel dosyası ({path}) okunamadı: {e}", exc_info=False)
        return None

    df.columns = df.columns.str.strip().str.lower()
    if len(df) < 252:
        log.debug(f"{path} kısa veri – atlandı")
        return None

    parquet_p = path.replace(".xlsx", ".parquet")
    if not os.path.exists(parquet_p):
        try:
            df.to_parquet(parquet_p)
        except Exception as e:
            log.warning(f"Parquet kaydedilemedi: {parquet_p}: {e}", exc_info=False)
    return df


def _standardize_date_column(
    df: pd.DataFrame, file_path_for_log: str = "", logger_param=None
) -> pd.DataFrame:
    log = logger_param or logger
    olasi_tarih_sutunlari = [
        "Tarih",
        "tarih",
        "TARİH",
        "Date",
        "date",
        "Zaman",
        "zaman",
    ]
    if not df.empty and df.columns[0].startswith("Unnamed:"):
        olasi_tarih_sutunlari.append(df.columns[0])

    bulunan_tarih_sutunu = None
    for col_name in olasi_tarih_sutunlari:
        if col_name in df.columns:
            bulunan_tarih_sutunu = col_name
            break

    if bulunan_tarih_sutunu:
        if bulunan_tarih_sutunu != "tarih":
            df.rename(columns={bulunan_tarih_sutunu: "tarih"}, inplace=True)
            log.debug(
                f"'{os.path.basename(file_path_for_log)}': Tarih sütunu '{bulunan_tarih_sutunu}' -> 'tarih' olarak adlandırıldı."
            )
        # else:
        # log.debug(f"'{os.path.basename(file_path_for_log)}': Tarih sütunu zaten 'tarih' adında.")
    else:
        log.warning(
            f"'{os.path.basename(file_path_for_log)}': Standart tarih sütunu ('Tarih' vb.) bulunamadı. Mevcut sütunlar: {df.columns.tolist()}"
        )
    return df


def _standardize_ohlcv_columns(
    df: pd.DataFrame, file_path_for_log: str = "", logger_param=None
) -> pd.DataFrame:
    log = logger_param or logger
    file_name_short = os.path.basename(
        file_path_for_log
    )  # Loglarda kısa dosya adı için
    log.debug(f"--- '{file_name_short}': OHLCV Standardizasyonu Başlıyor ---")
    log.debug(f"'{file_name_short}': Orijinal Sütunlar: {df.columns.tolist()}")

    rename_map = {}
    current_columns_set = set(df.columns)  # Anlık sütunları set olarak tut

    # config.OHLCV_MAP içindeki her bir (ham_ad_cfg: standart_ad_cfg) çifti için
    for raw_name_from_config, standard_name_target in config.OHLCV_MAP.items():
        # Eğer config'deki ham_ad DataFrame'in sütunları arasında varsa
        if raw_name_from_config in current_columns_set:
            # Ve bu ham_ad, zaten hedeflenen standart ad değilse
            # VE hedeflenen standart ad, DataFrame'de (rename_map ile oluşacaklar dahil) henüz yoksa
            # VEYA hedeflenen standart ad zaten rename_map'te başka bir orijinal adla eşleşmişse AMA şu anki raw_name_from_config için değilse
            if (
                raw_name_from_config != standard_name_target
                and (
                    standard_name_target not in current_columns_set
                    or standard_name_target not in df.columns
                )
                and standard_name_target not in rename_map.values()
            ):  # Bu standart ada daha önce başka bir sütun atanmamışsa
                rename_map[raw_name_from_config] = standard_name_target
                log.debug(
                    f"'{file_name_short}': Eşleştirme bulundu: '{raw_name_from_config}' -> '{standard_name_target}' (rename_map'e eklendi)"
                )
            elif raw_name_from_config == standard_name_target:
                pass  # log.debug(f"'{file_name_short}': Sütun '{raw_name_from_config}' zaten standart adında.")
            elif (
                standard_name_target in current_columns_set
                or standard_name_target in df.columns
            ):
                pass  # log.debug(f"'{file_name_short}': Hedef standart ad '{standard_name_target}' DataFrame'de zaten mevcut. '{raw_name_from_config}' için işlem yapılmadı.")
            elif standard_name_target in rename_map.values():
                pass  # log.debug(f"'{file_name_short}': Hedef standart ad '{standard_name_target}' zaten başka bir sütun için rename_map'te. '{raw_name_from_config}' için işlem yapılmadı.")
        # else:
        # log.debug(f"'{file_name_short}': Config'deki ham ad '{raw_name_from_config}' DataFrame'de bulunamadı.")

    if rename_map:
        log.info(
            f"'{file_name_short}': Uygulanacak yeniden adlandırma haritası: {rename_map}"
        )
        try:
            df.rename(columns=rename_map, inplace=True)
            log.info(
                f"'{file_name_short}': Yeniden adlandırma sonrası sütunlar: {df.columns.tolist()}"
            )
        except Exception as e_rename:
            log.error(
                f"'{file_name_short}': Sütunlar yeniden adlandırılırken HATA: {e_rename}. Harita: {rename_map}",
                exc_info=True,
            )
    else:
        log.debug(
            f"'{file_name_short}': OHLCV için yeniden adlandırılacak sütun bulunamadı (ya zaten standart ya da MAP'te eşleşme yok)."
        )

    # Son kontrol: Hedeflediğimiz standart sütunlar var mı?
    temel_hedef_sutunlar = ["open", "high", "low", "close", "volume"]
    mevcut_sutunlar_son_hali = set(df.columns)  # rename sonrası güncel sütunlar
    eksik_temel_sutunlar = [
        s for s in temel_hedef_sutunlar if s not in mevcut_sutunlar_son_hali
    ]

    if eksik_temel_sutunlar:
        log.warning(
            f"'{file_name_short}': Standartlaştırma sonrası TEMEL HEDEF OHLCV sütunlarından bazıları hala eksik: {eksik_temel_sutunlar}."
        )
    else:
        log.info(
            f"'{file_name_short}': Tüm temel hedef OHLCV sütunları ('open', 'high', 'low', 'close', 'volume') başarıyla oluşturuldu/bulundu."
        )
    log.debug(f"--- '{file_name_short}': OHLCV Standardizasyonu Tamamlandı ---")
    return df


def yukle_filtre_dosyasi(
    filtre_dosya_yolu_cfg=None, logger_param=None
) -> pd.DataFrame | None:
    fn_logger = logger_param or logger
    filtre_dosya_yolu = filtre_dosya_yolu_cfg or config.FILTRE_DOSYA_YOLU
    fn_logger.info(f"Filtre dosyası yükleniyor: {filtre_dosya_yolu}")

    if not os.path.exists(filtre_dosya_yolu):
        fn_logger.critical(
            f"FİLTRE DOSYASI BULUNAMADI: {filtre_dosya_yolu}. Sistem devam edemez."
        )
        return None
    try:
        df_filtreler = _cache_loader.load_csv(
            filtre_dosya_yolu,
            delimiter=";",
            engine="python",
            encoding="utf-8-sig",
            skipinitialspace=True,
        )
        fn_logger.info(
            f"Filtre dosyası '{filtre_dosya_yolu}' başarıyla yüklendi. {len(df_filtreler)} filtre bulundu."
        )
    except Exception as e:
        fn_logger.critical(
            f"Filtre dosyası ({filtre_dosya_yolu}) okunurken KRİTİK HATA: {e}. Sistem devam edemez.",
            exc_info=True,
        )
        return None

    if hasattr(config, "FILTRE_SUTUN_ADLARI_MAP"):
        df_filtreler.rename(
            columns=config.FILTRE_SUTUN_ADLARI_MAP, inplace=True, errors="ignore"
        )

    if (
        "FilterCode" not in df_filtreler.columns
        or "PythonQuery" not in df_filtreler.columns
    ):
        fn_logger.critical(
            f"Filtre dosyası ({filtre_dosya_yolu}) standart 'FilterCode' veya 'PythonQuery' sütunlarını içermiyor. Sistem devam edemez."
        )
        return None

    df_filtreler.dropna(subset=["PythonQuery"], inplace=True)
    df_filtreler = df_filtreler[
        df_filtreler["PythonQuery"].astype(str).str.strip() != ""
    ]
    fn_logger.debug(
        f"Yüklenen ve boş olmayan sorgulara sahip filtre sayısı: {len(df_filtreler)}"
    )
    return df_filtreler


def yukle_hisse_verileri(
    hisse_dosya_pattern_cfg=None,
    parquet_ana_dosya_yolu_cfg=None,
    force_excel_reload=False,
    logger_param=None,
) -> pd.DataFrame | None:
    fn_logger = logger_param or logger
    parquet_dosya_yolu = parquet_ana_dosya_yolu_cfg or config.PARQUET_ANA_DOSYA_YOLU
    hisse_dosya_pattern = hisse_dosya_pattern_cfg or config.HISSE_DOSYA_PATTERN
    veri_klasoru = config.VERI_KLASORU

    check_and_create_dirs(
        veri_klasoru,
        os.path.dirname(parquet_dosya_yolu) if parquet_dosya_yolu else None,
    )

    if (
        not force_excel_reload
        and parquet_dosya_yolu
        and os.path.exists(parquet_dosya_yolu)
    ):
        try:
            df_birlesik = pd.read_parquet(parquet_dosya_yolu)
            fn_logger.info(
                f"Birleşik hisse verileri Parquet dosyasından yüklendi: {parquet_dosya_yolu} ({len(df_birlesik)} satır)"
            )
            if not df_birlesik.empty and "hisse_kodu" in df_birlesik.columns:
                fn_logger.debug(
                    f"Parquet'ten yüklenen hisse kodları (ilk 5): {df_birlesik['hisse_kodu'].unique()[:5]}"
                )
            # Parquet'ten yüklenen verinin de sütunlarının kontrol edilmesi iyi bir pratik olabilir.
            # Ancak şu anki akışta standardizasyon CSV/Excel'den sonra yapılıyor.
            return df_birlesik
        except Exception as e:
            fn_logger.warning(
                f"Parquet dosyası ({parquet_dosya_yolu}) okunamadı, Excel/CSV'den yeniden yüklenecek. Hata: {e}",
                exc_info=False,
            )

    fn_logger.info(
        "Parquet dosyası bulunamadı/kullanılmadı veya zorla yeniden yükleme aktif. Kaynak CSV/Excel dosyaları okunacak..."
    )

    excel_dosyalari = glob.glob(os.path.join(veri_klasoru, "*.xlsx")) + glob.glob(
        os.path.join(veri_klasoru, "*.xls")
    )
    csv_dosyalari = glob.glob(hisse_dosya_pattern)

    filtre_dosya_tam_yolu_abs = os.path.abspath(config.FILTRE_DOSYA_YOLU)
    excel_dosyalari = [
        f
        for f in excel_dosyalari
        if os.path.abspath(f) != filtre_dosya_tam_yolu_abs
        and not os.path.basename(f).startswith("~$")
    ]
    csv_dosyalari = [
        f
        for f in csv_dosyalari
        if os.path.abspath(f) != filtre_dosya_tam_yolu_abs
        and not os.path.basename(f).startswith("~$")
    ]

    if not excel_dosyalari and not csv_dosyalari:
        fn_logger.critical(
            f"Belirtilen pattern'de ({hisse_dosya_pattern} ve Excel varyasyonları) kaynak veri dosyası bulunamadı ({veri_klasoru}). Sistem devam edemez."
        )
        return None

    tum_hisse_datalari = []
    for dosya_yolu in excel_dosyalari:
        hisse_kodu_excel = ""
        try:
            xls = _cache_loader.load_excel(dosya_yolu)
            for sayfa_adi in xls.sheet_names:
                hisse_kodu_excel = str(sayfa_adi).upper().strip()
                df_hisse = xls.parse(sayfa_adi)
                df_hisse = _standardize_date_column(df_hisse, dosya_yolu, fn_logger)
                df_hisse = _standardize_ohlcv_columns(
                    df_hisse, dosya_yolu, fn_logger
                )  # Dosya yolu log için eklendi
                df_hisse["hisse_kodu"] = hisse_kodu_excel
                tum_hisse_datalari.append(df_hisse)
        except Exception as e:
            fn_logger.error(
                f"Excel dosyası ({dosya_yolu} - Sayfa: {hisse_kodu_excel if hisse_kodu_excel else 'BILINMIYOR'}) işlenirken hata: {e}",
                exc_info=False,
            )

    for dosya_yolu in csv_dosyalari:
        hisse_kodu_csv = ""
        try:
            base_name = os.path.basename(dosya_yolu)
            hisse_kodu_csv = os.path.splitext(base_name)[0]
            if ".xlsx - " in hisse_kodu_csv:
                hisse_kodu_csv = hisse_kodu_csv.split(".xlsx - ")[-1]

            df_hisse = _cache_loader.load_csv(
                dosya_yolu,
                delimiter=None,
                engine="python",
                encoding="utf-8-sig",
                skipinitialspace=True,
            )
            df_hisse = _standardize_date_column(
                df_hisse, dosya_yolu, fn_logger
            )  # Dosya yolu log için eklendi
            df_hisse = _standardize_ohlcv_columns(
                df_hisse, dosya_yolu, fn_logger
            )  # Dosya yolu log için eklendi
            df_hisse["hisse_kodu"] = str(hisse_kodu_csv).upper().strip()
            tum_hisse_datalari.append(df_hisse)
        except Exception as e:
            fn_logger.error(
                f"CSV dosyası ({dosya_yolu} - Hisse Kodu Tahmini: {hisse_kodu_csv}) işlenirken hata: {e}",
                exc_info=False,
            )

    if not tum_hisse_datalari:
        fn_logger.critical("Hiçbir hisse verisi yüklenemedi. Sistem devam edemez.")
        return None

    try:
        df_birlesik = pd.concat(tum_hisse_datalari, ignore_index=True)
        fn_logger.info(
            f"Toplam {len(df_birlesik)} satır ve {df_birlesik['hisse_kodu'].nunique()} farklı hisse verisi birleştirildi."
        )
    except Exception as e:
        fn_logger.critical(
            f"Hisse verileri birleştirilirken KRİTİK HATA: {e}. Sistem devam edemez.",
            exc_info=True,
        )
        return None

    # Birleştirilmiş DataFrame'in sütunlarını son bir kez logla (Parquet'e yazmadan önce)
    fn_logger.debug(
        f"Birleştirilmiş DataFrame (Parquet'e yazılmadan önce) sütunları: {df_birlesik.columns.tolist()}"
    )

    if not df_birlesik.empty and parquet_dosya_yolu:
        try:
            gerekli_sutunlar_parquet = [
                "tarih",
                "open",
                "high",
                "low",
                "close",
                "volume",
                "hisse_kodu",
            ]
            eksik_sutunlar_kayit_oncesi = [
                s for s in gerekli_sutunlar_parquet if s not in df_birlesik.columns
            ]
            if eksik_sutunlar_kayit_oncesi:
                fn_logger.warning(
                    f"Parquet'e kaydetmeden önce birleştirilmiş DataFrame'de temel sütunlar eksik: {eksik_sutunlar_kayit_oncesi}. Bu durum sorunlara yol açabilir."
                )
            else:
                fn_logger.debug(
                    "Parquet'e kaydetmeden önce tüm temel sütunlar birleşik DataFrame'de mevcut."
                )

            df_birlesik.to_parquet(parquet_dosya_yolu, index=False)
            fn_logger.info(
                f"Birleşik hisse verileri Parquet olarak kaydedildi: {parquet_dosya_yolu}"
            )
        except Exception as e:
            fn_logger.error(
                f"Parquet dosyası ({parquet_dosya_yolu}) kaydedilemedi: {e}",
                exc_info=False,
            )

    return df_birlesik
