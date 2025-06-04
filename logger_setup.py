# logger_setup.py
# -*- coding: utf-8 -*-
# Proje: Finansal Analiz ve Backtest Sistemi Geliştirme
# Modül: Merkezi Loglama Yapılandırması
# Tuğrul Karaaslan & Gemini
# Tarih: 18 Mayıs 2025 (Kod kalitesi için yorumlar eklendi)

import logging
import sys
import os
try:
    import config # Ana yapılandırma dosyasını import et
except ImportError:
    # Eğer config.py import edilemezse (örn: bu dosya tek başına çalıştırılırsa),
    # temel bir loglama yapılandırması kullan.
    class ConfigMock:
        """config.py yüklenemediğinde kullanılacak sahte config sınıfı."""
        LOG_LEVEL = logging.DEBUG
        LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s [%(filename)s:%(lineno)d] - %(process)d - %(threadName)s - %(message)s'
        LOG_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
        # Acil durum log dosyasının doğrudan scriptin çalıştığı dizine yazılması planlanabilir.
        LOG_DOSYA_YOLU = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'acil_durum_finansal_analiz.log')

    config = ConfigMock()
    print(f"UYARI: config.py yüklenemedi, acil durum loglama ayarları kullanılıyor. Log dosyası: {config.LOG_DOSYA_YOLU}", file=sys.stderr)

_loggers = {} # Oluşturulan logger'ları saklamak için global bir sözlük

def get_logger(name='FinansalAnalizSistemi'):
    """
    Belirtilen isimle bir logger nesnesi alır veya oluşturur.
    Logger'lar _loggers sözlüğünde saklanarak aynı isimle tekrar tekrar handler eklenmesi önlenir.

    Args:
        name (str): Logger'a verilecek isim.

    Returns:
        logging.Logger: Yapılandırılmış logger nesnesi.
    """
    if name in _loggers:
        return _loggers[name] # Eğer logger zaten varsa, mevcut olanı döndür

    logger = logging.getLogger(name) # Yeni bir logger nesnesi oluştur veya al

    # Handler'ların sadece bir kere (logger ilk oluşturulduğunda) eklenmesini sağla
    if not logger.handlers:
        logger.setLevel(config.LOG_LEVEL) # Log seviyesini config'den al
        formatter = logging.Formatter(config.LOG_FORMAT, datefmt=config.LOG_DATE_FORMAT) # Log formatını config'den al

        # Konsol (stdout) için handler
        ch = logging.StreamHandler(sys.stdout)
        ch.setFormatter(formatter)
        logger.addHandler(ch)

        # Dosya için handler
        try:
            log_file_path = config.LOG_DOSYA_YOLU
            log_dir = os.path.dirname(log_file_path)
            if log_dir and not os.path.exists(log_dir): # Log klasörü yoksa oluştur
                os.makedirs(log_dir, exist_ok=True)
                logger.info(f"Log dizini oluşturuldu: {log_dir}")

            fh = logging.FileHandler(log_file_path, mode='a', encoding='utf-8') # 'a' moduyla dosyanın sonuna ekle
            fh.setFormatter(formatter)
            logger.addHandler(fh)
        except Exception as e:
            # Bu kritik bir hata, çünkü log dosyasına yazılamıyor.
            # Standart stderr'e yazarak kullanıcıyı bilgilendir.
            print(f"KRİTİK LOGGER HATASI: Log dosyası ({getattr(config, 'LOG_DOSYA_YOLU', 'Bilinmiyor')}) oluşturulamadı/yazılamadı: {e}", file=sys.stderr)

    _loggers[name] = logger # Oluşturulan logger'ı sözlüğe ekle
    return logger

if __name__ == '__main__':
    # Bu dosya doğrudan çalıştırıldığında bir test logger'ı oluşturur.
    test_logger = get_logger('LoggerSetupTest')
    test_logger.debug("Bu bir logger_setup DEBUG mesajıdır.")
    test_logger.info("Bu bir logger_setup INFO mesajıdır.")
    test_logger.warning("Bu bir logger_setup WARNING mesajıdır.")
    test_logger.error("Bu bir logger_setup ERROR mesajıdır.")
    test_logger.critical("Bu bir logger_setup CRITICAL mesajıdır.")
