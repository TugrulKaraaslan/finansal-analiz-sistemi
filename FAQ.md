# SSS

- **Veri dosyalarını nereye koyarım?** Tüm dosyalar `data/` altına; ayrıntı için [Yol & Veri Sorunları](TROUBLESHOOT.md#yol-veri-sorunlari).
- **`DATA_DIR` nasıl değişir?** Ortam değişkeni ile ayarla, [bkz. Yol & Veri Sorunları](TROUBLESHOOT.md#yol-veri-sorunlari).
- **`EXCEL_DIR` neyi kontrol eder?** Excel kaynak klasörünü; [Yol & Veri Sorunları](TROUBLESHOOT.md#yol-veri-sorunlari).
- **`alias_mapping.csv` nedir?** Alias ↔ kanonik eşlemesi; [Alias & Sembol Eşleşmeleri](TROUBLESHOOT.md#alias-sembol).
- **`BIST.xlsx` eksikse ne yaparım?** Örnek dosyayı `data/`ya kopyala; [Yol & Veri Sorunları](TROUBLESHOOT.md#yol-veri-sorunlari).
- **CLI komutları nereden öğrenirim?** `python -m backtest.cli --help`; sorunlar için [CLI Hataları](TROUBLESHOOT.md#cli-hatalari).
- **Tarih formatı ne olmalı?** ISO `YYYY-MM-DD`; [CLI Hataları](TROUBLESHOOT.md#cli-hatalari).
- **Filtre modülü bulunamıyor, neden?** Modül yolu yanlış; [Yol & Veri Sorunları](TROUBLESHOOT.md#yol-veri-sorunlari).
- **`ModuleNotFoundError: openpyxl` ne demek?** Excel motoru eksik; [Excel/CSV/Parquet Okuma Hataları](TROUBLESHOOT.md#excel-hatalari).
- **Büyük Excel dosyaları yavaş mı?** Parquet'e dönüştür; [Excel/CSV/Parquet Okuma Hataları](TROUBLESHOOT.md#excel-hatalari).
- **Parquet'e nasıl dönüştürürüm?** `convert-to-parquet` komutunu kullan; [Excel/CSV/Parquet Okuma Hataları](TROUBLESHOOT.md#excel-hatalari).
- **Alias eşleşmesi yoksa?** `alias_mapping.csv`ye satır ekle; [Alias & Sembol Eşleşmeleri](TROUBLESHOOT.md#alias-sembol).
- **Testleri nasıl çalıştırırım?** `pytest -q`; [Test & CI](TROUBLESHOOT.md#test-ci).
- **Log dosyalarını nerede bulurum?** `loglar/` dizininde; [Günlükler & Log Seviyesi](TROUBLESHOOT.md#gunlukler-log-seviyesi).
- **Windows'ta yol uzunluğu hatası ne?** 260 karakter sınırı; [OS/İzin/Path Uzunluğu](TROUBLESHOOT.md#os-izin).
- **Colab veya farklı sürücüde `data/` yolu?** `DATA_DIR` ile mutlak yol ver; [Yol & Veri Sorunları](TROUBLESHOOT.md#yol-veri-sorunlari).
