# Sorun Giderme

## Hızlı Tanı Akışı <a id="tani-akisi"></a>
1. `python -m backtest.cli --help` çalışıyor mu? → Hayır: [CLI Hataları](#cli-hatalari)
2. Çalışma dizininde `data/` var mı? → Hayır: [Yol & Veri Sorunları](#yol-veri-sorunlari)
3. `DATA_DIR` veya `EXCEL_DIR` yanlış mı? → Evet: [Yol & Veri Sorunları](#yol-veri-sorunlari)
4. `BIST.xlsx` ve `alias_mapping.csv` mevcut mu? → Hayır: [Yol & Veri Sorunları](#yol-veri-sorunlari)
5. CLI argümanları eksik mi? → Evet: [CLI Hataları](#cli-hatalari)
6. Excel/CSV okuma hatası mı alınıyor? → Evet: [Excel/CSV/Parquet Okuma Hataları](#excel-hatalari)
7. Alias eşleşmesi başarısız mı? → Evet: [Alias & Sembol Eşleşmeleri](#alias-sembol)
8. Hâlâ çözülemedi mi? → Logları kontrol et: [Günlükler & Log Seviyesi](#gunlukler-log-seviyesi)

### Komut örnekleri
```bash
python -m backtest.cli --help
python -m backtest.cli dry-run --filters filters.csv
python -m backtest.cli convert-to-parquet --out data_parquet
```

## Yol & Veri Sorunları <a id="yol-veri-sorunlari"></a>

### `data/` dizini yok
- **Belirti/Mesaj**: `FileNotFoundError: .../data`
- **Muhtemel Neden(ler)**: Klasör silinmiş veya farklı dizindesiniz.
- **Çözüm Adımları**:
  ```bash
  mkdir -p data
  ```
- **Doğrulama**:
  ```bash
  python - <<'PY'
  from pathlib import Path; import sys
  p = Path('data'); print('EXISTS:', p.exists(), 'ABS:', p.resolve())
  PY
  ```

### `BIST.xlsx` veya `alias_mapping.csv` eksik
- **Belirti/Mesaj**: `FileNotFoundError: 'data/BIST.xlsx'`
- **Muhtemel Neden(ler)**: Örnek dosyalar taşınmış.
- **Çözüm Adımları**: Depo kökündeki `data/` dizinine uygun dosyaları kopyalayın.
- **Doğrulama**:
  ```bash
  ls data/BIST.xlsx data/alias_mapping.csv
  ```

### `DATA_DIR`/`EXCEL_DIR` yanlış
- **Belirti/Mesaj**: CLI veriyi bulamıyor veya boş sonuç döndürür.
- **Muhtemel Neden(ler)**: Ortam değişkenleri hatalı; Windows/Colab bağlaçları.
- **Çözüm Adımları**:
  ```bash
  export DATA_DIR=/mutlak/yol/data
  export EXCEL_DIR=/mutlak/yol/excel
  ```
- **Doğrulama**:
  ```bash
  echo $DATA_DIR; echo $EXCEL_DIR
  ```

## Excel/CSV/Parquet Okuma Hataları <a id="excel-hatalari"></a>

### `ModuleNotFoundError: openpyxl`
- **Belirti/Mesaj**: `ModuleNotFoundError: No module named 'openpyxl'`
- **Muhtemel Neden(ler)**: Excel okuma motoru yüklü değil.
- **Çözüm Adımları**:
  ```bash
  pip install openpyxl
  ```
- **Doğrulama**:
  ```bash
  python - <<'PY'
  import openpyxl, pandas as pd
  pd.read_excel('data/BIST.xlsx')
  PY
  ```

### Şema veya dtype uyuşmazlığı
- **Belirti/Mesaj**: `ValueError: could not convert string to float`
- **Muhtemel Neden(ler)**: Ondalık ayracı veya tarih formatı farklı.
- **Çözüm Adımları**: Veriyi `convert-to-parquet` ile dönüştürün; `decimal=','` gibi parametreleri ayarlayın.
- **Doğrulama**:
  ```bash
  python -m backtest.cli convert-to-parquet --out data_parquet
  ls data_parquet
  ```

## Alias & Sembol Eşleşmeleri <a id="alias-sembol"></a>

### Eşleşmeyen sembol
- **Belirti/Mesaj**: `ValueError: alias bulunamadı: XYZ`
- **Muhtemel Neden(ler)**: `alias_mapping.csv` satırı eksik veya hatalı.
- **Çözüm Adımları**: Dosyaya `XYZ,XYZ` (alias,kanonik) satırı ekleyin.
- **Doğrulama**:
  ```bash
  grep '^XYZ,' data/alias_mapping.csv
  ```

## CLI Hataları <a id="cli-hatalari"></a>

### `error: the following arguments are required`
- **Belirti/Mesaj**: `error: the following arguments are required: --start, --end`
- **Muhtemel Neden(ler)**: Gerekli argümanlar verilmemiş.
- **Çözüm Adımları**:
  ```bash
  python -m backtest.cli scan-range --start 2024-01-01 --end 2024-01-05 \
    --data data/BIST.xlsx --filters filters.csv --out raporlar
  ```
- **Doğrulama**: Komut başarıyla tamamlanır ve `raporlar/` dizini oluşur.

### Tarih biçimi hataları
- **Belirti/Mesaj**: `ValueError: time data '01-31-2024' does not match format`
- **Muhtemel Neden(ler)**: ISO `YYYY-MM-DD` formatı kullanılmamış.
- **Çözüm Adımları**: Tarihleri `2024-01-31` biçiminde yazın.
- **Doğrulama**: CLI komutları hata vermeden çalışır.

## Test & CI <a id="test-ci"></a>

### `pytest` ağ isteği deniyor
- **Belirti/Mesaj**: Testler ağ erişimine çalışıyor.
- **Muhtemel Neden(ler)**: Testlerde ağ çağrıları engellenmemiş.
- **Çözüm Adımları**: Ağ erişimini mock'layın veya ilgili testi skip edin.
- **Doğrulama**:
  ```bash
  pytest -q
  ```

### Fixture yolu bulunamıyor
- **Belirti/Mesaj**: `FileNotFoundError: tests/data/...`
- **Muhtemel Neden(ler)**: Yanlış çalışma dizini.
- **Çözüm Adımları**: `pytest -q` komutunu depo kökünden çalıştırın.
- **Doğrulama**: Testler yolu bulur ve geçer.

## OS/İzin/Path Uzunluğu <a id="os-izin"></a>

### PermissionError veya uzun yol hataları
- **Belirti/Mesaj**: `PermissionError: [Errno 13]` veya Windows'ta `OSError: [WinError 206]`
- **Muhtemel Neden(ler)**: Windows dosya kilidi, 260 karakter sınırı veya mount izinleri.
- **Çözüm Adımları**: Kısa yollar kullanın (`C:\proj`), dosyaları kapattığınızdan emin olun; Linux'ta izinleri düzeltin.
- **Doğrulama**: İşlem yeniden denendiğinde hata alınmaz.

## Günlükler & Log Seviyesi <a id="gunlukler-log-seviyesi"></a>

### Loglar nereye yazılır?
- **Belirti/Mesaj**: Çalışma sırasında neler olduğunu görmek istiyorum.
- **Muhtemel Neden(ler)**: Log seviyesi düşük veya dizin bilinmiyor.
- **Çözüm Adımları**:
  ```bash
  python -m backtest.cli scan-day --data data/BIST.xlsx --filters filters.csv \
    --date 2024-01-02 --out raporlar --log-level DEBUG
  ```
  Loglar varsayılan olarak `loglar/` dizinine yazılır.
- **Doğrulama**:
  ```bash
  ls loglar
  ```
