# filter_engine.py
# -*- coding: utf-8 -*-
# Proje: Finansal Analiz ve Backtest Sistemi Geliştirme
# Modül: Filtreleme Motoru
# Tuğrul Karaaslan & Gemini
# Tarih: 18 Mayıs 2025 (Loglama ve hata yönetimi iyileştirmeleri)

import pandas as pd
import re
import keyword

from filtre_dogrulama import SEBEP_KODLARI


def _extract_query_columns(query: str) -> set:
    tokens = set(re.findall(r"[A-Za-z_][A-Za-z0-9_]*", query))
    reserved = set(keyword.kwlist) | {"and", "or", "not", "True", "False", "df"}
    return tokens - reserved


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
    logger.warning(
        "logger_setup.py bulunamadı, filter_engine.py standart logging kullanıyor."
    )


def uygula_filtreler(
    df_ana_veri: pd.DataFrame,
    df_filtre_kurallari: pd.DataFrame,
    tarama_tarihi: pd.Timestamp,
    logger_param=None,
) -> tuple[dict, dict]:
    """
    Verilen ana veri üzerinde, filtre kurallarını kullanarak hisseleri tarar.

    Args:
        df_ana_veri (pd.DataFrame): İndikatörleri hesaplanmış tüm hisse verilerini içeren DataFrame.
        df_filtre_kurallari (pd.DataFrame): 'FilterCode' ve 'PythonQuery' sütunlarını içeren DataFrame.
        tarama_tarihi (pd.Timestamp): Hangi tarihteki verilere göre tarama yapılacağı.
        logger_param: Kullanılacak logger nesnesi (opsiyonel).

    Returns:
        tuple[dict, dict]:
            - filtre_sonuclar: {
                filtre_kodu: {
                    "hisseler": list[str],
                    "sebep": str,
                    "hisse_sayisi": int,
                }
            }
            - atlanmis_filtreler_log_dict: {filtre_kodu: hata_mesajı}
    """
    fn_logger = logger_param or get_logger(f"{__name__}.uygula_filtreler")
    fn_logger.info(
        f"Filtreleme işlemi başlatılıyor. Tarama Tarihi: {tarama_tarihi.strftime('%d.%m.%Y')}"
    )

    if df_ana_veri is None or df_ana_veri.empty:
        fn_logger.error(
            "Filtreleme için ana veri (df_ana_veri) boş veya None. İşlem durduruluyor."
        )
        return {}, {
            "TUM_FILTRELER_ATLADI": "Filtreleme için ana veri (df_ana_veri) boş veya None."
        }

    if "hisse_kodu" not in df_ana_veri.columns or "tarih" not in df_ana_veri.columns:
        fn_logger.error(
            f"Ana veride 'hisse_kodu' veya 'tarih' sütunları eksik. Filtreleme yapılamaz. Mevcut sütunlar: {df_ana_veri.columns.tolist()}"
        )
        return {}, {
            "TUM_FILTRELER_ATLADI": "Ana veride hisse_kodu veya tarih sütunu eksik."
        }

    try:
        # Tarih sütununun datetime olduğundan emin ol
        if not pd.api.types.is_datetime64_any_dtype(df_ana_veri["tarih"]):
            df_ana_veri["tarih"] = pd.to_datetime(df_ana_veri["tarih"], errors="coerce")

        # Sadece tarama gününe ait veriyi al ve üzerinde çalışmak için kopyala
        df_tarama_gunu = df_ana_veri[df_ana_veri["tarih"] == tarama_tarihi].copy()
        if df_tarama_gunu.empty:
            prev = df_ana_veri[df_ana_veri["tarih"] < tarama_tarihi]["tarih"].max()
            if pd.notna(prev):
                fn_logger.info(
                    f"{tarama_tarihi.strftime('%d.%m.%Y')} yok → {prev.strftime('%d.%m.%Y')} kullanıldı"
                )
                df_tarama_gunu = df_ana_veri[df_ana_veri["tarih"] == prev].copy()
                tarama_tarihi = prev
            else:
                fn_logger.warning(
                    f"Belirtilen tarama tarihi ({tarama_tarihi.strftime('%d.%m.%Y')}) ve öncesi için veri yok."
                )
                return {}, {
                    "TUM_FILTRELER_ATLADI": f'Tarama tarihinde ({tarama_tarihi.strftime("%d.%m.%Y")}) ve önceki günlerde veri yok.'
                }
    except Exception as e_tarih_hazirlik:
        fn_logger.error(
            f"Filtreleme için tarama günü verisi hazırlanırken hata: {e_tarih_hazirlik}",
            exc_info=True,
        )
        return {}, {
            "TUM_FILTRELER_ATLADI": f"Tarama günü verisi hazırlama hatası: {e_tarih_hazirlik}"
        }

    if df_tarama_gunu.empty:
        fn_logger.warning(
            f"Belirtilen tarama tarihi ({tarama_tarihi.strftime('%d.%m.%Y')}) için ana veride hiç kayıt bulunamadı."
        )
        return {}, {
            "TUM_FILTRELER_ATLADI": f'Tarama tarihinde ({tarama_tarihi.strftime("%d.%m.%Y")}) veri yok.'
        }

    fn_logger.info(
        f"Tarama gününe ({tarama_tarihi.strftime('%d.%m.%Y')}) ait {len(df_tarama_gunu)} hisse satırı (benzersiz hisse sayısı: {df_tarama_gunu['hisse_kodu'].nunique()}) üzerinde filtreler uygulanacak."
    )
    fn_logger.debug(
        f"Tarama günü DataFrame sütunları (ilk 10): {df_tarama_gunu.columns.tolist()[:10]}"
    )

    filtre_sonuclar = {}
    atlanmis_filtreler_log_dict = {}

    for index, row in df_filtre_kurallari.iterrows():
        filtre_kodu = row.get("FilterCode", f"FiltreIndex_{index}")
        python_sorgusu_raw = row.get("PythonQuery")

        if pd.isna(python_sorgusu_raw) or not str(python_sorgusu_raw).strip():
            fn_logger.warning(
                f"Filtre '{filtre_kodu}': Python sorgusu boş veya NaN, atlanıyor."
            )
            atlanmis_filtreler_log_dict[filtre_kodu] = "Python sorgusu boş veya NaN."
            filtre_sonuclar[filtre_kodu] = {
                "hisseler": [],
                "sebep": "NO_STOCK",
                "hisse_sayisi": 0,
            }
            continue

        python_sorgusu = str(python_sorgusu_raw)
        sorgu_strip = python_sorgusu.strip()
        if re.search(r"\b(?:and|or)\s*$", sorgu_strip) or sorgu_strip.endswith(
            (">", "<", "=", "(", "&", "|")
        ):
            hata_mesaji = (
                f"Sorgu olası eksik ifade ile bitiyor, atlandı: '{python_sorgusu}'"
            )
            fn_logger.error(f"Filtre '{filtre_kodu}': {hata_mesaji}")
            atlanmis_filtreler_log_dict[filtre_kodu] = hata_mesaji
            filtre_sonuclar[filtre_kodu] = {
                "hisseler": [],
                "sebep": "QUERY_ERROR",
                "hisse_sayisi": 0,
            }
            continue
        kullanilan_sutunlar = _extract_query_columns(python_sorgusu)
        eksik_sutunlar = [
            s for s in kullanilan_sutunlar if s not in df_tarama_gunu.columns
        ]
        if (
            "volume_tl" in eksik_sutunlar
            and {"volume", "close"} <= set(df_tarama_gunu.columns)
        ):
            df_tarama_gunu["volume_tl"] = (
                df_tarama_gunu["volume"] * df_tarama_gunu["close"]
            )
            eksik_sutunlar = [
                s for s in kullanilan_sutunlar if s not in df_tarama_gunu.columns
            ]
        if {"psar_long", "psar_short"} <= set(
            df_tarama_gunu.columns
        ) and "psar" in eksik_sutunlar:
            # psar_long/short varsa birleşik psar hesaplanmamış; uyar, devam et
            df_tarama_gunu["psar"] = df_tarama_gunu["psar_long"].fillna(
                df_tarama_gunu["psar_short"]
            )
            eksik_sutunlar = [
                s for s in kullanilan_sutunlar if s not in df_tarama_gunu.columns
            ]
        if eksik_sutunlar:
            hata_mesaji = f"Eksik sütunlar: {', '.join(eksik_sutunlar)}"
            fn_logger.error(f"Filtre '{filtre_kodu}' sorgusunda {hata_mesaji}.")
            atlanmis_filtreler_log_dict[filtre_kodu] = hata_mesaji
            filtre_sonuclar[filtre_kodu] = {
                "hisseler": [],
                "sebep": "MISSING_COL",
                "hisse_sayisi": 0,
            }
            continue

        try:
            # Sorguyu çalıştırmadan önce mevcut sütunları logla (DEBUG için)
            fn_logger.debug(
                f"Filtre '{filtre_kodu}' uygulanıyor. Sorgu: '{python_sorgusu}'. df_tarama_gunu sütunları: {df_tarama_gunu.columns.tolist()}"
            )
            filtrelenmis_df = df_tarama_gunu.query(
                python_sorgusu,
                engine="python",
                local_dict=df_tarama_gunu.to_dict("series"),
            )

            if not filtrelenmis_df.empty:
                hisse_kodlari_listesi = filtrelenmis_df["hisse_kodu"].unique().tolist()
                sebep_kodu = "OK"
                fn_logger.info(
                    f"Filtre '{filtre_kodu}': {len(hisse_kodlari_listesi)} hisse bulundu. (Örnek: {hisse_kodlari_listesi[:3]})"
                )
            else:
                hisse_kodlari_listesi = []
                sebep_kodu = "NO_STOCK"
                fn_logger.debug(f"Filtre '{filtre_kodu}': Uygun hisse bulunamadı.")

            filtre_sonuclar[filtre_kodu] = {
                "hisseler": hisse_kodlari_listesi,
                "sebep": sebep_kodu,
                "hisse_sayisi": len(hisse_kodlari_listesi),
            }

        except pd.errors.UndefinedVariableError as e_undef_var:
            # Hata mesajından hangi değişkenin/sütunun tanımsız olduğunu ayıkla
            tanimsiz_degisken = (
                str(e_undef_var).split("'")[1]
                if "'" in str(e_undef_var)
                else "Bilinmeyen"
            )
            hata_mesaji = f"Tanımsız sütun/değişken: '{tanimsiz_degisken}'. Sorgu: '{python_sorgusu}'"
            fn_logger.error(
                f"Filtre '{filtre_kodu}' sorgusunda TANIMSIZ DEĞİŞKEN/SÜTUN hatası: {hata_mesaji}",
                exc_info=False,
            )
            atlanmis_filtreler_log_dict[filtre_kodu] = hata_mesaji
            filtre_sonuclar[filtre_kodu] = {
                "hisseler": [],
                "sebep": "MISSING_COL",
                "hisse_sayisi": 0,
            }
        except SyntaxError as e_syntax:
            hata_mesaji = (
                "Syntax (yazım) hatası. Sorgu: "
                f"'{python_sorgusu}'. Muhtemelen eksik karşılaştırma operatörü veya parantez."
                " Filtre dosyanızı gözden geçirin."
            )
            fn_logger.error(
                f"Filtre '{filtre_kodu}' sorgusunda SYNTAX HATASI: {e_syntax}. {hata_mesaji}",
                exc_info=False,
            )
            atlanmis_filtreler_log_dict[filtre_kodu] = hata_mesaji
            filtre_sonuclar[filtre_kodu] = {
                "hisseler": [],
                "sebep": "QUERY_ERROR",
                "hisse_sayisi": 0,
            }
        except Exception as e_query:  # Diğer olası query hataları
            hata_mesaji = (
                f"Sorgu uygulanırken beklenmedik hata. Sorgu: '{python_sorgusu}'"
            )
            fn_logger.error(
                f"Filtre '{filtre_kodu}' uygulanırken BEKLENMEDİK HATA: {e_query}. {hata_mesaji}",
                exc_info=True,
            )
            atlanmis_filtreler_log_dict[filtre_kodu] = f"{hata_mesaji} Detay: {e_query}"
            filtre_sonuclar[filtre_kodu] = {
                "hisseler": [],
                "sebep": "QUERY_ERROR",
                "hisse_sayisi": 0,
            }

    fn_logger.info(
        f"Tüm filtreler uygulandı. {len(filtre_sonuclar)} filtre için sonuç listesi üretildi."
    )
    if atlanmis_filtreler_log_dict:
        fn_logger.warning(
            f"Atlanan/hatalı filtre sayısı: {len(atlanmis_filtreler_log_dict)}. Detaylar için bir sonraki log seviyesine bakınız veya raporu inceleyiniz."
        )
        for fk, err_msg in atlanmis_filtreler_log_dict.items():
            fn_logger.debug(f"  Atlanan/Hatalı Filtre '{fk}': {err_msg}")

    return filtre_sonuclar, atlanmis_filtreler_log_dict
