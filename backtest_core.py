# backtest_core.py
# -*- coding: utf-8 -*-
# Proje: Finansal Analiz ve Backtest Sistemi Geliştirme
# Modül: Basit Backtest Motoru
# Tuğrul Karaaslan & Gemini
# Tarih: 18 Mayıs 2025 (Loglama iyileştirmeleri, not yönetimi)

import pandas as pd
import numpy as np
import config

try:
    from logger_setup import get_logger
    logger = get_logger(__name__)
except ImportError:
    import logging
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)
    logger.warning("logger_setup.py bulunamadı, backtest_core.py standart logging kullanıyor.")

def _get_fiyat(df_hisse_veri: pd.DataFrame, tarih: pd.Timestamp, zaman_sutun_adi: str, logger_param=None) -> float:
    """Belirli bir hisse için, verilen tarihteki ve zamandaki (sütun adı) fiyatı alır."""
    log = logger_param or logger
    hisse_kodu_log = df_hisse_veri['hisse_kodu'].iloc[0] if not df_hisse_veri.empty and 'hisse_kodu' in df_hisse_veri.columns else 'Bilinmeyen Hisse'

    try:
        # Tarih sütununun datetime olduğundan emin ol (preprocessor bunu yapmalı)
        if not pd.api.types.is_datetime64_any_dtype(df_hisse_veri['tarih']):
            df_hisse_veri['tarih'] = pd.to_datetime(df_hisse_veri['tarih'], errors='coerce')

        veri_satiri = df_hisse_veri[df_hisse_veri['tarih'] == tarih]
        if veri_satiri.empty:
            # log.debug(f"{hisse_kodu_log} için {tarih.strftime('%d.%m.%Y')} tarihinde veri bulunamadı ({zaman_sutun_adi} için).")
            return np.nan

        if zaman_sutun_adi in veri_satiri.columns:
            fiyat = veri_satiri[zaman_sutun_adi].iloc[0]
            if pd.notna(fiyat):
                try:
                    return float(fiyat)
                except ValueError: # Sayıya çevrilemiyorsa
                    log.warning(f"'{zaman_sutun_adi}' sütunundaki değer ('{fiyat}') float'a çevrilemedi. Hisse: {hisse_kodu_log}, Tarih: {tarih.strftime('%d.%m.%Y')}")
                    return np.nan
            # log.debug(f"Fiyat '{zaman_sutun_adi}' sütununda NaN bulundu. Hisse: {hisse_kodu_log}, Tarih: {tarih.strftime('%d.%m.%Y')}")
            return np.nan # Fiyat NaN ise NaN döndür
        else:
            log.warning(f"Fiyat almak için beklenen sütun '{zaman_sutun_adi}' bulunamadı. Hisse: {hisse_kodu_log}, Tarih: {tarih.strftime('%d.%m.%Y')}. Mevcut Sütunlar: {df_hisse_veri.columns.tolist()}")
            return np.nan
    except Exception as e:
        log.error(f"{hisse_kodu_log} için fiyat alınırken ({tarih.strftime('%d.%m.%Y')} {zaman_sutun_adi}) hata: {e}", exc_info=False)
        return np.nan

def calistir_basit_backtest(filtrelenmis_hisseler: dict,
                            df_tum_veri: pd.DataFrame,
                            satis_tarihi_str: str,
                            tarama_tarihi_str: str,
                            atlanmis_filtre_loglari: dict | None = None, # None olabileceğini belirt
                            logger_param=None) -> dict:
    """
    Filtrelenmiş hisseler üzerinde basit bir al-sat simülasyonu yapar ve getirileri hesaplar.
    """
    fn_logger = logger_param or get_logger(f"{__name__}.calistir_basit_backtest")
    fn_logger.info(f"Basit backtest çalıştırılıyor. Tarama: {tarama_tarihi_str}, Satış: {satis_tarihi_str}")

    if df_tum_veri is None or df_tum_veri.empty:
        fn_logger.error("Backtest için ana veri (df_tum_veri) boş veya None. İşlem durduruluyor.")
        return {} # Boş dict döndür

    try:
        satis_tarihi = pd.to_datetime(satis_tarihi_str, format='%d.%m.%Y')
        tarama_tarihi = pd.to_datetime(tarama_tarihi_str, format='%d.%m.%Y')
    except ValueError:
        fn_logger.critical(f"Satış tarihi '{satis_tarihi_str}' veya tarama tarihi '{tarama_tarihi_str}' geçerli bir formatta (dd.mm.yyyy) değil. Backtest durduruluyor.")
        return {}

    # config'den alım/satım zamanı ve komisyonu al
    alim_fiyat_sutunu = config.ALIM_ZAMANI # örn: 'open'
    satis_fiyat_sutunu = config.SATIS_ZAMANI # örn: 'open' veya 'close'
    komisyon_orani = config.KOMISYON_ORANI
    strateji_adi = getattr(config, "UYGULANAN_STRATEJI", "basit_backtest")

    genel_sonuclar_dict = {}
    istisnalar = []

    # Eğer bazı filtreler atlanmışsa, rapor için bunları başlangıçta ekle
    if atlanmis_filtre_loglari:
        for filtre_kodu, log_mesaji in atlanmis_filtre_loglari.items():
            if filtre_kodu not in genel_sonuclar_dict: # Sadece daha önce eklenmemişse
                 genel_sonuclar_dict[filtre_kodu] = {
                    'hisse_sayisi': 0,
                    'islem_yapilan_sayisi': 0,
                    'ortalama_getiri': np.nan,
                    'hisse_performanslari': pd.DataFrame(columns=['hisse_kodu', 'alis_fiyati', 'satis_fiyati', 'getiri_yuzde', 'not']),
                    'notlar': [str(log_mesaji)] # Gelen mesajı stringe çevir
                }

    # Filtrelenmiş hisseler üzerinde dön
    if not filtrelenmis_hisseler and not atlanmis_filtre_loglari:
        fn_logger.warning("Filtrelenmiş hisse bulunmuyor ve atlanmış filtre logu da yok. Backtest için işlenecek veri yok.")
        # return genel_sonuclar_dict, istisnalar # Zaten boş olacak

    for filtre_kodu, hisse_kodlari_listesi in filtrelenmis_hisseler.items():
        fn_logger.debug(f"--- Filtre: '{filtre_kodu}' için backtest başlıyor ---")

        # Not listesini mevcut sözlükten referans olarak al; yoksa giriş oluştur
        if filtre_kodu not in genel_sonuclar_dict:
            genel_sonuclar_dict[filtre_kodu] = {
                'hisse_sayisi': 0,
                'islem_yapilan_sayisi': 0,
                'ortalama_getiri': np.nan,
                'hisse_performanslari': pd.DataFrame(columns=['hisse_kodu', 'alis_fiyati', 'satis_fiyati', 'getiri_yuzde', 'not']),
                'notlar': []
            }

        current_filtre_notlari = genel_sonuclar_dict[filtre_kodu]['notlar']

        if not hisse_kodlari_listesi: # Eğer bu filtre için hisse listesi boşsa
            if not any("Bu filtreye uyan hisse yok." in note for note in current_filtre_notlari):
                current_filtre_notlari.append("Bu filtreye uyan hisse yok.")

            # genel_sonuclar_dict'te bu filtre için bir giriş oluştur veya güncelle
            genel_sonuclar_dict[filtre_kodu].update({
                'hisse_sayisi': 0,
                'islem_yapilan_sayisi': 0,
                'ortalama_getiri': np.nan,
                'hisse_performanslari': pd.DataFrame(columns=['hisse_kodu', 'alis_fiyati', 'satis_fiyati', 'getiri_yuzde', 'not'])
            })
            genel_sonuclar_dict[filtre_kodu]['notlar'] = list(set(current_filtre_notlari))
            continue # Sonraki filtreye geç

        bireysel_performanslar = []
        hisse_sayisi_filtreye_uyan = len(hisse_kodlari_listesi)
        # fn_logger.info(f"Filtre '{filtre_kodu}': {hisse_sayisi_filtreye_uyan} hisse için işlem yapılacak.")

        for hisse_adi in hisse_kodlari_listesi:
            df_hisse_ozel = df_tum_veri[df_tum_veri['hisse_kodu'] == hisse_adi].copy()
            if df_hisse_ozel.empty:
                # fn_logger.warning(f"'{hisse_adi}' için ana veride kayıt bulunamadı.")
                bireysel_performanslar.append({
                    'hisse_kodu': hisse_adi,
                    'alis_fiyati': np.nan,
                    'satis_fiyati': np.nan,
                    'getiri_yuzde': np.nan,
                    'not': 'Veri Yok',
                    'alis_tarihi': tarama_tarihi.strftime('%d.%m.%Y'),
                    'satis_tarihi': satis_tarihi.strftime('%d.%m.%Y'),
                    'uygulanan_strateji': strateji_adi
                })
                continue

            alis_fiyati = satis_fiyati = getiri_yuzde = np.nan
            hisse_notu = ""

            try:
                alis_fiyati = _get_fiyat(df_hisse_ozel, tarama_tarihi, alim_fiyat_sutunu, fn_logger)
                satis_fiyati = _get_fiyat(df_hisse_ozel, satis_tarihi, satis_fiyat_sutunu, fn_logger)

                if pd.notna(alis_fiyati) and pd.notna(satis_fiyati):
                    if alis_fiyati > 0: # Alış fiyatı pozitif olmalı
                        net_alis_fiyati = alis_fiyati * (1 + komisyon_orani)
                        net_satis_fiyati = satis_fiyati * (1 - komisyon_orani)
                        if net_alis_fiyati > 0: # Net alış fiyatı da pozitif olmalı
                            getiri_yuzde = ((net_satis_fiyati - net_alis_fiyati) / net_alis_fiyati) * 100
                            hisse_notu = "Başarılı"
                        else:
                            hisse_notu = "Net alış fiyatı sıfır veya negatif."
                    else:
                        hisse_notu = "Alış fiyatı sıfır veya negatif."
                elif pd.isna(alis_fiyati):
                    hisse_notu = f"Alış fiyatı ({alim_fiyat_sutunu}) bulunamadı ({tarama_tarihi.strftime('%d.%m.%Y')})."
                elif pd.isna(satis_fiyati):
                    hisse_notu = f"Satış fiyatı ({satis_fiyat_sutunu}) bulunamadı ({satis_tarihi.strftime('%d.%m.%Y')})."
                # fn_logger.debug(f"{hisse_adi}: Alış: {alis_fiyati}, Satış: {satis_fiyati}, Getiri: {getiri_yuzde if pd.notna(getiri_yuzde) else '-'}")
            except Exception as e_hisse_backtest:
                hisse_notu = f"Backtest sırasında hata: {e_hisse_backtest}"
                fn_logger.error(f"{hisse_adi} için backtest hatası: {e_hisse_backtest}", exc_info=False)

            if pd.isna(alis_fiyati) or pd.isna(satis_fiyati):
                istisnalar.append({
                    "filtre_kodu": filtre_kodu,
                    "hisse_kodu": hisse_adi,
                    "neden": "Alış veya satış fiyatı eksik"
                })

            bireysel_performanslar.append({
                'hisse_kodu': hisse_adi,
                'alis_fiyati': round(alis_fiyati,2) if pd.notna(alis_fiyati) else np.nan,
                'satis_fiyati': round(satis_fiyati,2) if pd.notna(satis_fiyati) else np.nan,
                'getiri_yuzde': round(getiri_yuzde, 2) if pd.notna(getiri_yuzde) else np.nan,
                'not': hisse_notu,
                'alis_tarihi': tarama_tarihi.strftime('%d.%m.%Y'),
                'satis_tarihi': satis_tarihi.strftime('%d.%m.%Y'),
                'uygulanan_strateji': strateji_adi
            })

        df_performans = pd.DataFrame(bireysel_performanslar)
        gecerli_getiriler = df_performans['getiri_yuzde'].dropna()
        ortalama_getiri = gecerli_getiriler.mean() if not gecerli_getiriler.empty else np.nan

        # Notları topla
        if not df_performans.empty:
            basarisiz_notlar = df_performans[df_performans['not'] != 'Başarılı']['not'].unique().tolist()
            if basarisiz_notlar:
                current_filtre_notlari.extend(basarisiz_notlar)
        elif hisse_sayisi_filtreye_uyan > 0: # Hisse vardı ama performans df'i boş kaldıysa (hepsinde veri yoksa vs.)
            current_filtre_notlari.append("Filtreye uyan hisseler için performans verisi üretilemedi.")

        if not current_filtre_notlari: # Eğer hiç not yoksa (başarılı atlanmış veya hisse yok notu dahil)
            if hisse_sayisi_filtreye_uyan > 0 and len(gecerli_getiriler) == 0:
                current_filtre_notlari.append("Tüm hisseler için alım/satım fiyatı bulunamadı veya getiri hesaplanamadı.")
            elif hisse_sayisi_filtreye_uyan > 0 and len(gecerli_getiriler) > 0:
                 current_filtre_notlari.append("Tüm işlemler başarılı veya ek not yok.")
            # Eğer hisse_sayisi_filtreye_uyan == 0 ise zaten en başta "Bu filtreye uyan hisse yok" notu eklenmişti.

        genel_sonuclar_dict[filtre_kodu].update({
            'hisse_sayisi': hisse_sayisi_filtreye_uyan,
            'islem_yapilan_sayisi': len(gecerli_getiriler),
            'ortalama_getiri': round(ortalama_getiri, 2) if pd.notna(ortalama_getiri) else np.nan,
            'hisse_performanslari': df_performans
        })
        genel_sonuclar_dict[filtre_kodu]['notlar'] = list(set(current_filtre_notlari))

    fn_logger.info("Tüm filtreler için basit backtest tamamlandı.")
    return genel_sonuclar_dict, istisnalar
