# Finansal Analiz Sistemi

## Amaç
- BIST verileri üzerinde filtre bazlı tarama ile T→T+1 getirilerini analiz eder.
- Yeni kullanıcıların 2 dk içinde ilk sonuçlarını alması hedeflenir.

## Klasör Yapısı
| Yol | Açıklama |
| --- | --- |
| backtest/ | Komut satırı arayüzü ve analiz motoru |
| utils/ | Ortak yardımcı fonksiyonlar |
| examples/ | Örnek config ve tatil dosyası |
| Veri/ | Excel fiyat dosyalarının konacağı klasör |
| tests/ | Birim testleri |
| filters.csv | Filtre tanımları |

## Filtre CSV Açıklaması
- Satırlar `;` ile ayrılır.
- Kolonlar:

| Kolon | Açıklama |
| ----- | ----- |
| FilterCode | Filtrenin raporda görünecek kısa adı |
| PythonQuery | `pandas` ifadesi, örn: `(rsi_14 > 65) and (relative_volume > 1)` |
| Group *(opsiyonel)* | Filtreleri kategorize etmek için kullanılabilir |

- Örnek satır:
```csv
T24;(rsi_14 > 65) and (relative_volume > 1.0)
```

## Kurulum ve Çalıştırma
### Yerel
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python -m backtest.cli scan-day --config examples/example_config.yaml --date 2024-01-02
```
### Google Colab
```python
!pip install -q -r requirements_colab.txt
!python -m backtest.cli scan-day --config examples/example_config.yaml --date 2024-01-02
```

## Örnek Çalıştırma
- `examples/example_config.yaml` içindeki `excel_dir` ve `filters_csv` yollarını düzenleyin.
- Tek gün tarama:
```bash
python -m backtest.cli scan-day --config examples/example_config.yaml --date 2025-03-07
```

## Çıktı Açıklaması
- Excel: `raporlar/{start}_{end}_1G_BIST100.xlsx`
- Sheet'ler:
  - `SCAN_YYYY-MM-DD`: Günlük sonuçlar
  - `SUMMARY`: Dönemsel ortalamalar
- CSV kopyaları `raporlar/csv/` altında tutulur.
- Konsol örneği:
```
SCAN 2024-01-02: 24 satır, ort. %1.2
```
## Test Çalıştırma
```bash
pytest -q
```


## Backtest Akış Rehberi
1. **Veri Yükleme:** `backtest.data_loader.read_excels_long` ile Excel fiyat dosyalarını okuyun. Gerekirse `backtest.calendars.add_next_close_calendar` ile işlem günlerine göre `next_date` ve `next_close` alanlarını ekleyin.
2. **İndikatör Hesabı:** `indicator_calculator.py` veya benzeri bir araçla göstergeleri hesaplayın ve veri ile birleştirin. `backtest.indicators.compute_indicators` fonksiyonu varsayılan olarak yerleşik (`builtin`) hesaplayıcıyı kullanır. `pandas_ta` kütüphanesini kurup `engine="pandas_ta"` parametresini geçerseniz, kütüphane mevcutsa otomatik olarak kullanılacak; değilse yerleşik yöntemlere geri dönecektir.
3. **Filtreleme:** `backtest.screener.run_screener` fonksiyonunu kullanarak `filters.csv` içindeki sorguları çalıştırın.
4. **Getiri Hesabı:** Filtre sonuçlarını `backtest.backtester.run_1g_returns` fonksiyonuna vererek T+N getirilerini hesaplayın. Tatil ve hafta sonu hatalarını önlemek için `trading_days` parametresine işlem günlerini geçin.
5. **Raporlama:** Çıktıları `backtest.reporter.write_reports` veya `backtest.report.write_report` aracılığıyla Excel/CSV olarak kaydedin.

## Sürüm Notları
- 1.1.0: Colab desteği ve yeni README.
- 1.0.0: İlk yayımlanan sürüm.

