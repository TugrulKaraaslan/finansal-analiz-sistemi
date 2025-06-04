# main.py
# -*- coding: utf-8 -*-
# Proje: Finansal Analiz ve Backtest Sistemi Geliştirme
# Ana Çalıştırma Script'i
# Tuğrul Karaaslan & Gemini
# Tarih: 18 Mayıs 2025 (Erken hata durdurma mantığı eklendi, loglama iyileştirildi)

import pandas as pd
import sys
import os
import logging # logger_setup'tan önce temel logging için
import config # Önce config'i import et, logger_setup ondan sonra gelsin

# Logger'ı mümkün olan en erken aşamada yapılandır
try:
    from logger_setup import get_logger
    # main.py'nin kendi adıyla bir logger oluştur
    logger = get_logger(os.path.splitext(os.path.basename(__file__))[0])
except ImportError as e_log_setup:
    # logger_setup.py bulunamazsa, çok temel bir fallback
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
    logger = logging.getLogger("main_fallback_logger")
    logger.critical(f"KRİTİK HATA: logger_setup.py import edilemedi: {e_log_setup}. Temel logging kullanılıyor.", exc_info=True)
    # Bu durumda config.LOG_DOSYA_YOLU kullanılamaz, loglar sadece konsola gider.
except Exception as e_logger_init:
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
    logger = logging.getLogger("main_fallback_logger_init_error")
    logger.critical(f"KRİTİK HATA: Logger başlatılırken hata: {e_logger_init}. Temel logging kullanılıyor.", exc_info=True)
    # Bu durumda da config.LOG_DOSYA_YOLU kullanılamaz.

# Ana modülleri import et
try:
    import data_loader
    import preprocessor
    import indicator_calculator
    import filter_engine
    import backtest_core
    import report_generator
    logger.info("Tüm ana modüller başarıyla import edildi.")
except ImportError as e_import_main:
    logger.critical(f"Temel modüllerden biri import edilemedi: {e_import_main}. Sistem durduruluyor.", exc_info=True)
    sys.exit(1) # Kritik hata, devam etme

def calistir_tum_sistemi(tarama_tarihi_str: str,
    satis_tarihi_str: str,
    force_excel_reload_param: bool = False,
    logger_param=None):
    """
    Finansal analiz ve backtest sisteminin tüm adımlarını çalıştırır.
    """
    # Eğer dışarıdan bir logger verilmediyse, bu fonksiyon kendi adıyla bir alt logger oluşturur.
    # Ancak genellikle main_logger (yukarıda tanımlanan) buraya logger_param olarak verilir.
    fn_logger = logger_param or get_logger(f"{__name__}.calistir_tum_sistemi")

    fn_logger.info("*" * 30 + " TÜM BACKTEST SİSTEMİ ÇALIŞTIRILIYOR " + "*" * 30)
    fn_logger.info(f"  Tarama Tarihi            : {tarama_tarihi_str}")
    fn_logger.info(f"  Satış Tarihi             : {satis_tarihi_str}")
    fn_logger.info(f"  Excel/CSV'den Zorla Yükle: {force_excel_reload_param}")
    fn_logger.info("-" * 80)

    # Adım 1: Veri Girişi (Filtreler ve Ham Hisse Verisi)
    fn_logger.info("[Adım 1/6] Veri Girişi (data_loader) Başlatılıyor...")
    df_filtre_kurallari = data_loader.yukle_filtre_dosyasi(logger_param=fn_logger)
    if df_filtre_kurallari is None or df_filtre_kurallari.empty:
        fn_logger.critical("Filtre kuralları yüklenemedi veya boş. Sistem durduruluyor.")
        return None

    df_ana_veri_ham = data_loader.yukle_hisse_verileri(
    force_excel_reload=force_excel_reload_param, logger_param=fn_logger
    )
    if df_ana_veri_ham is None or df_ana_veri_ham.empty:
        fn_logger.critical("Hisse verileri yüklenemedi veya boş. Sistem durduruluyor.")
        return None
    fn_logger.info(f"[Adım 1/6] Veri Girişi Tamamlandı. {len(df_ana_veri_ham)} ham kayıt, {len(df_filtre_kurallari)} filtre kuralı.")
    fn_logger.info("-" * 80)

    # Adım 2: Veri Ön İşleme
    fn_logger.info("[Adım 2/6] Veri Ön İşleme (preprocessor) Başlatılıyor...")
    df_islenmis_veri = preprocessor.on_isle_hisse_verileri(df_ana_veri_ham, logger_param=fn_logger)
    if df_islenmis_veri is None or df_islenmis_veri.empty:
        fn_logger.critical("Veri ön işleme adımında kritik hata veya boş sonuç. Sistem durduruluyor.")
        return None

    # Ön işleme sonrası temel OHLCV sütunlarının varlığını kontrol et
    temel_ohlcv_kontrol = ['open', 'high', 'low', 'close', 'volume']
    eksik_on_isleme_sonrasi = [s for s in temel_ohlcv_kontrol if s not in df_islenmis_veri.columns]
    if eksik_on_isleme_sonrasi:
        fn_logger.critical(f"Ön işleme sonrası temel OHLCV sütunları hala eksik: {eksik_on_isleme_sonrasi}. Sistem durduruluyor.")
        return None
    fn_logger.info(f"[Adım 2/6] Veri Ön İşleme Tamamlandı. {len(df_islenmis_veri)} işlenmiş kayıt.")
    fn_logger.info("-" * 80)

    # Adım 3: İndikatör ve Kesişim Hesaplama
    fn_logger.info("[Adım 3/6] İndikatör ve Kesişim Hesaplama (indicator_calculator) Başlatılıyor...")
    df_data_indikatorlu = indicator_calculator.hesapla_teknik_indikatorler_ve_kesisimler(df_islenmis_veri, logger_param=fn_logger)
    if df_data_indikatorlu is None or df_data_indikatorlu.empty:
        fn_logger.error("İndikatör hesaplama adımında kritik hata veya boş sonuç. Filtreleme ve backtest yapılamayacak.")
        # Burada sistemi tamamen durdurmak yerine, raporlamada bu durumu belirtecek şekilde devam edebiliriz.
        # Ancak filtrelenmis_hisseler_dict boş olacağı için backtest de boş olacaktır.
        # Şimdilik, eğer indikatörlü veri yoksa, boş bir dict ile devam edelim ki raporlama en azından hata loglarını yazabilsin.
        filtrelenmis_hisseler_dict = {}
        atlanmis_filtreler = {'TUM_FILTRELER_INDİKATORSUZ_VERI': 'İndikatörlü veri üretilemediği için tüm filtreler atlandı.'}
    else:
        fn_logger.info("[Adım 3/6] Teknik İndikatör ve Kesişim Hesaplama Tamamlandı.")
        fn_logger.debug(f"Indicator calculator sonrası df_data_indikatorlu sütun sayısı: {len(df_data_indikatorlu.columns)}")
        fn_logger.info("-" * 80)

    # Adım 4: Filtre Uygulama
    fn_logger.info("[Adım 4/6] Filtre Uygulama (filter_engine) Başlatılıyor...")
    try:
        tarama_tarihi_dt = pd.to_datetime(tarama_tarihi_str, format='%d.%m.%Y')
    except ValueError:
        fn_logger.critical(
            f"Tarama tarihi '{tarama_tarihi_str}' geçerli bir formatta (dd.mm.yyyy) değil. Sistem durduruluyor."
        )
        return None

    filtrelenmis_hisseler_dict, atlanmis_filtreler = filter_engine.uygula_filtreler(
    df_data_indikatorlu, df_filtre_kurallari, tarama_tarihi_dt, logger_param=fn_logger
    )
    if not filtrelenmis_hisseler_dict and not atlanmis_filtreler:
        fn_logger.warning("Filtreleme sonucu hem filtrelenmiş hisse üretmedi hem de atlanmış filtre bilgisi boş.")
    elif not filtrelenmis_hisseler_dict:
        fn_logger.info("Filtreleme sonucu hiçbir hisse bulunamadı.")
    fn_logger.info(f"[Adım 4/6] Filtre Uygulama Tamamlandı. {len(filtrelenmis_hisseler_dict)} filtre sonucu üretildi.")

    fn_logger.info("-" * 80)

    # Adım 5: Backtest Çalıştırma
    fn_logger.info("[Adım 5/6] Basit Backtest Çalıştırma (backtest_core) Başlatılıyor...")
    # df_data_indikatorlu None veya boş olabilir, backtest_core bunu handle etmeli
backtest_sonuclari = backtest_core.calistir_basit_backtest(
    filtrelenmis_hisseler=filtrelenmis_hisseler_dict,  # Boş olabilir
    df_tum_veri=df_data_indikatorlu,  # None veya boş olabilir
    satis_tarihi_str=satis_tarihi_str,
    tarama_tarihi_str=tarama_tarihi_str,
    atlanmis_filtre_loglari=atlanmis_filtreler,  # Boş olabilir
    logger_param=fn_logger,
)
# Tuple dönerse unpack et
if isinstance(backtest_sonuclari, tuple):
    backtest_sonuclari, istisnalar = backtest_sonuclari
else:
    istisnalar = []
    if not backtest_sonuclari: # Eğer backtest_core boş dict döndürürse (örn: kritik hata)
        fn_logger.warning("Backtest çalıştırma sonucu boş. Rapor bu duruma göre oluşturulacak.")
    fn_logger.info("[Adım 5/6] Basit Backtest Çalıştırma Tamamlandı.")
    fn_logger.info("-" * 80)

    # Adım 6: Rapor Oluşturma
    fn_logger.info("[Adım 6/6] Özet Rapor Oluşturma (report_generator) Başlatılıyor...")
    if backtest_sonuclari is not None:
        report_generator.olustur_ozet_rapor(
            sonuclar_listesi=[
                {
                    'filtre_kodu': k,
                    'ortalama_getiri': v['ortalama_getiri'],
                    'tarama_tarihi': tarama_tarihi_str,
                    'satis_tarihi': satis_tarihi_str,
                    'hisseler': v['hisse_performanslari'].to_dict('records'),
                    'notlar': v.get('notlar', [])
                } for k, v in backtest_sonuclari.items()
            ],
    cikti_klasoru=os.path.join(config.CIKTI_KLASORU, "raporlar"),
    logger=fn_logger
    )
    else:
        fn_logger.error("Backtest sonuçları None geldiği için CSV raporu oluşturulamayacak.")

    # Bu satırlar artık `else`'in içinde değil — if-else sonrası kapanış logları
    fn_logger.info("[Adım 6/6] Özet Rapor Oluşturma Tamamlandı.")
    fn_logger.info("=" * 80)
    fn_logger.info("TÜM SİSTEM ÇALIŞMASI TAMAMLANDI.")
    fn_logger.info("=" * 80)

    return backtest_sonuclari



if __name__ == '__main__':
    logger.info("="*80)
    logger.info(f"======= {os.path.basename(__file__).upper()} ANA BACKTEST SCRIPT BAŞLATILIYOR =======")
    try:
        logger.info(f"Çalışma Zamanı: {pd.Timestamp.now(tz=config.TIMEZONE)}")
        logger.info(f"Python Sürümü: {sys.version.split()[0]}, Pandas Sürümü: {pd.__version__}")
        logger.info(f"config.py Yolu: {os.path.abspath(config.__file__)}")
    except Exception as e_startup_info:
        logger.warning(f"Başlangıç bilgileri loglanırken hata: {e_startup_info}")
    logger.info("="*80)

    tarama_t = config.TARAMA_TARIHI_DEFAULT
    satis_t = config.SATIS_TARIHI_DEFAULT

    logger.info("Varsayılan Parametrelerle Çalıştırılıyor:")
    logger.info(f"  Tarama Tarihi    : {tarama_t}")
    logger.info(f"  Satış Tarihi     : {satis_t}")
    logger.info("="*80 + "\n")

    try:
        # Ana sistemi çalıştır ve logger'ı main.py'nin kendi logger'ı olarak ilet
        sistem_sonuclari = calistir_tum_sistemi(
            tarama_tarihi_str=tarama_t,
            satis_tarihi_str=satis_t,
            force_excel_reload_param=False, # İlk çalıştırmada False, gerekirse True yapılır
            logger_param=logger
        )

        if sistem_sonuclari is not None:
            logger.info("İŞLEM SONUÇLARI ALINDI.")
            if not sistem_sonuclari or all(not v.get('hisse_performanslari', pd.DataFrame()).shape[0] for v in sistem_sonuclari.values()):
                 logger.info("Backtest sonuçları üretilemedi veya hiçbir filtre/hisse için işlem yapılamadı.")
            else:
                logger.info("Backtest başarıyla tamamlandı ve sonuçlar üretildi.")
        else:
            logger.error("Ana sistem çalıştırması KRİTİK bir hata nedeniyle None sonuç döndürdü. Detaylı hatalar için logları kontrol edin.")

    except Exception as e_main_run:
        logger.critical(f"Ana çalıştırma (`if __name__ == '__main__':`) bloğunda BEKLENMEDİK KRİTİK HATA: {e_main_run}", exc_info=True)
    finally:
        logger.info(f"======= {os.path.basename(__file__).upper()} ANA BACKTEST SCRIPT TAMAMLANDI =======")
        logging.shutdown() # Tüm logger handler'larını kapat
