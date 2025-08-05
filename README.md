
# BIST Backtest Projesi — 1G (T Kapanış → T+1 Kapanış)
**Amaç:** 01.01.2022’den itibaren filtre bazlı tarama ile **1 günlük ortalama getiri** ve **BIST farkı** analizi.  
**Çıktı:** Günlük sonuç **ayrı sheet**, dönemsel özet **tek sheet** (Excel); CSV kopyaları.

## Kurulum (Yerel)
```bash
python -m venv .venv && source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Hızlı Başlangıç
1) `examples/example_config.yaml` dosyasındaki yolları düzenleyin (`excel_dir`, `filters_csv`).  
2) Çalıştırın:
```bash
python -m backtest.cli scan-range --config examples/example_config.yaml --start 2024-01-01 --end 2025-01-01
```
Veya tek gün:
```bash
python -m backtest.cli scan-day --config examples/example_config.yaml --date 2025-03-07
```

## Veri & Filtre Dosyaları
- **Excel**: 13 dosya, her biri çoklu sheet; sheet adı **sembol** kabul edilir.  
- **Filtre CSV**: Kolonlar **FilterCode**, **PythonQuery**. Örnek:
```csv
FilterCode,PythonQuery
T24,(rsi_14 > 65) and (relative_volume > 1.0)
```

## Raporlar
- Excel: `raporlar/{start}_{end}_1G_BIST100.xlsx`  
  - Sheet’ler: `SCAN_YYYY-MM-DD` + `SUMMARY` (+ `SUMMARY_DIFF`, `BIST` opsiyonel)  
- CSV: `raporlar/csv/` klasöründe kopyalar.

## Teknik Ayrıntılar
- **T+1**: Fiyat tabanlı (her sembolde bir sonraki satır). Tatiller/hafta sonu otomatik atlanır.  
- **Göstergeler**: `pandas-ta` ile RSI/EMA/MACD + yardımcı kolonlar (relative_volume, change_%).  
- **Screener**: PythonQuery içindeki `and/or/not` ifadeleri otomatik `&/|/~`’e çevrilir ve pandas ile değerlendirilir.  
- **Backtester**: `ReturnPct = (T+1 close / T close - 1) * 100`.  
- **Benchmark**: (opsiyonel) `benchmark.load_xu100_pct("XU100.csv")` ile BIST% — `SUMMARY_DIFF` sheet’inde **Filtre − BIST**.

## En İyi Pratikler
- Büyük aralıklarda **xlsxwriter** engine ile daha hızlı yazım.  
- Çok günlük/pivot yoğun işlerde **Polars** ile ara tablo, Excel öncesi pandas’a dönüş.  
- Başlık normalize haritasını `config.price_schema` ile genişletin.

## Sorun Giderme
- `ModuleNotFoundError: TA-Lib`: Bu sürüm TA-Lib **gerektirmez**; `pandas-ta` kullanılır.  
- Excel’de yavaş yazım: `XlsxWriter` kullanın (requirements’ta var).  
- Bellek hatası: Aralığı parçalara bölün veya Polars’ı aktifleştirin.

## Colab
```python
!pip install -q pandas pandas-ta polars pyarrow XlsxWriter click pydantic loguru tqdm pyyaml openpyxl
!python -m backtest.cli scan-range --config examples/example_config.yaml --start 2024-01-01 --end 2024-03-01
```

## Lisans
MIT

## Colab — Tek Hücre Başlatıcı
```python
!unzip -o backtest_project_v1_1_stageA.zip -d /content/
%cd /content/backtest_project
!pip -q install numpy==1.26.4 pandas==2.2.2 pandas-ta==0.3.14b0                polars==1.4.0 pyarrow==16.0 XlsxWriter==3.2 openpyxl==3.1                click==8.1 tqdm==4.66 pydantic==2.7 loguru==0.7 PyYAML==6.0
!mkdir -p Veri
# Excel'leri Veri/ altına, filtre dosyasını köke 'filters.csv' adıyla koyun.
!PYTHONPATH=. python -m backtest.cli scan-range --config examples/example_config.yaml --start 2024-01-02 --end 2024-01-05
```

## T+1 Modları
- `price` (varsayılan): Sembol bazlı bir sonraki bar. Askıya alma/eksik günlerde **T+2** olabilir.
- `calendar`: Pazar günleri ve tatiller hariç **takvim T+1**; sembol T+1'de işlem görmediyse `next_close` NaN → o işlem **rapora dahil edilmez**.

`examples/holidays_tr.csv` ile tatilleri besleyebilirsiniz:
```yaml
calendar:
  tplus1_mode: "calendar"
  holidays_source: "csv"
  holidays_csv_path: "examples/holidays_tr.csv"
```

## Doğrulama Raporu
Çıktı Excel'inde şu ek sayfalar oluşturulur:
- `VALIDATION_SUMMARY`: sembol başına satır sayısı, ilk/son tarih, NA/duplicated.
- `VALIDATION_ISSUES`: negatif/0 kapanış, tarih sırası sorunları vb.

## Önbellek (Parquet) — İsteğe Bağlı
Büyük veri setlerinde Excel okuma maliyetini azaltmak için:
```yaml
data:
  enable_cache: true
  cache_parquet_path: "cache/prices.parquet"
```
İlk çalıştırmada Parquet üretilir; sonraki çalıştırmalarda doğrudan buradan yüklenir.

## BIST CSV Esneklik
`benchmark.load_xu100_pct()` tarih ve kapanış kolon adlarını **esnek** algılar; TR tarih biçimlerini (`dd.mm.yyyy`) ve `;` ayracı / `,` ondalık ayracını otomatik dener.


**Not:** Paket içinde boş `Veri/` klasörü hazır. Excel dosyalarınızı bu klasöre kopyalayın.
