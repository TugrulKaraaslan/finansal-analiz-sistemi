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

## İndikatör Kolonları ve Örnek Filtreler
Aşağıdaki tablo bazı sık kullanılan indikatör kolonlarını ve bunlara ilişkin örnek filtreleri gösterir:

| Kolon(lar) | Açıklama | Örnek Filtre |
| --- | --- | --- |
| `rsi_14` | 14 periyotluk Relative Strength Index | `(rsi_14 > 70)` (aşırı alım) |
| `ema_20`, `ema_50` | 20 ve 50 periyotluk üstel hareketli ortalamalar | `ema_20_keser_ema_50_yukari` (yukarı kesişim) |
| `macd_line`, `macd_signal` | MACD göstergesi ana ve sinyal çizgisi | `macd_line > macd_signal` |
| `stochrsi_k`, `stochrsi_d` | Stokastik RSI çizgileri | `stochrsi_k_keser_stochrsi_d_yukari` |

## Filtre CSV Açıklaması
- Satırlar `;` ile ayrılır.
- Kolonlar:

| Kolon | Açıklama |
| ----- | ----- |
| FilterCode | Filtrenin raporda görünecek kısa adı |
| PythonQuery | `pandas` ifadesi, örn: `(rsi_14 > 65) and (relative_volume > 1)` |
| Group *(opsiyonel)* | Filtreleri kategorize etmek için kullanılabilir |
| Side *(opsiyonel)* | İşlem yönü (`long`/`short`), belirtilmezse `long` varsayılır |

- Örnek tablo:

| FilterCode | PythonQuery | Group | Side |
| --- | --- | --- | --- |
| RSI70 | `(rsi_14 > 70)` | Momentum | long |
| EMA20_50 | `ema_20_keser_ema_50_yukari` | Trend | long |
| RSI30_SHORT | `rsi_14_keser_30p0_asagi` | Momentum | short |

## Kurulum ve Çalıştırma
### Yerel
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt -c constraints.txt --only-binary=:all: --no-binary=pandas-ta
pip install -r requirements_dev.txt -c constraints.txt --only-binary=:all: --no-binary=pandas-ta  # test/geliştirici ortamı
```

Python 3.10–3.12 sürümleri desteklenir; 3.13 henüz destek dışıdır.

Excel dosyalarını okuyup yazmak için gerekli `openpyxl` ve `XlsxWriter` paketleri de bu gereksinimlerle kurulur.

Spacy, fastai ve fastdownload bağımlılıkları kaldırılmış olup kurulmasına gerek yoktur.

```bash
python -m backtest.cli scan-day --config examples/example_config.yaml --date 2024-01-02
```
### Google Colab
```python
!pip install -q -r requirements_colab.txt -c constraints.txt --only-binary=:all: --no-binary=pandas-ta
# Uygun wheel bulunamazsa veya pandas_ta uyumsuzluğu olursa:
!pip install "numpy<2.0" "pandas<2.2" pandas-ta==0.3.14b0
!python -m backtest.cli scan-day --config config/colab_config.yaml --date 2024-01-02
```

> Not: Filtre CSV doğrulaması için [Pandera](https://pandera.readthedocs.io/) gerekir.
> Geliştiriciler `requirements_dev.txt` ile kurulmuş olur.

### Config Şeması Örneği

Aşağıdaki YAML şeması minimum zorunlu alanları gösterir:

```yaml
project:
  out_dir: raporlar
data:
  excel_dir: Veri  # fiyat excellerinin klasörü
  filters_csv: filters.csv  # filtre tanımları
```

`data.excel_dir` ve `data.filters_csv` alanları eksikse komut satırında
`config.data.* zorunlu; örnek için examples/example_config.yaml` şeklinde
bir hata mesajı gösterilir.

### Gösterge Motoru Davranışı

- Varsayılan olarak `pandas_ta` yüklüyse ve NumPy sürümüyle uyumluysa
  göstergeler bu motor ile hesaplanır.
- `pandas_ta` eksik veya NumPy 2 ile uyumsuzsa otomatik olarak yerleşik
  hesaplamalara dönülür. Konsolda örnek mesaj:

  ```
  compute_indicators using engine=builtin
  ```

### Var Olan Kolonların Korunması

- Mevcut bir kolon üzerine yazılmaz; `relative_volume` ya da
  `hacim_goreli` veride zaten varsa yeniden hesaplanmaz ve alias üretilmez.
- Çoklu kolon → tek kolon kopyalama hataları engellenir; uygun olmayan
  durumlar `alias skipped` uyarısı ile geçilir.
- `pd.concat` sonrası oluşan mükerrer kolon adları tekilleştirilir ve
  logda listelenir.

### Hazır Gösterge Kolonları ve Kesişimler

- Veride indikatör kolonları önceden hesaplanmışsa `indicators.engine: "none"`
  ayarıyla hesaplama adımı tamamen atlanır.
- Sistem, tanımlı kolonlardan otomatik olarak kesişim alanları üretir; örn.
  `sma_10_keser_sma_50_yukari` veya `adx_14_keser_20p0_asagi`.
- Eksik kaynak kolonlar işlem akışını durdurmaz, sadece uyarı logu bırakılır.

Örnek config parçası:

```yaml
indicators:
  engine: "none"
  params: {}
project:
  stop_on_filter_error: false  # eksik kolonda filtreyi atla
```

## Örnek Çalıştırma
- `examples/example_config.yaml` içindeki `excel_dir` ve `filters_csv` yollarını düzenleyin.
- Tek gün tarama:
```bash
python -m backtest.cli scan-day --config examples/example_config.yaml --date 2025-03-07
```

### Config ile Çok Gün Aralığı Örneği
Linux ortamında `Veri` klasör adının büyük harfle yazıldığına dikkat edin.

```bash
python -m backtest.cli scan-range \
  --config examples/example_config.yaml \
  --start 2025-03-07 \
  --end   2025-03-11 \
  --holding-period 1 \
  --transaction-cost 0.0005
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
## Test Çalıştırma (isteğe bağlı)
```bash
pip install -r requirements_dev.txt -c constraints.txt --only-binary=:all: --no-binary=pandas-ta
pytest -q
```

## Benchmark

| Fonksiyon | Satır (n) | Süre (ms) |
| --- | --- | --- |
| `compute_indicators` | 1000 | ~17 |
| `run_1g_returns` | 1000 | ~24 |


## Backtest Akış Rehberi
1. **Veri Yükleme:** `backtest.data_loader.read_excels_long` ile Excel fiyat dosyalarını okuyun. Gerekirse `backtest.calendars.add_next_close_calendar` ile işlem günlerine göre `next_date` ve `next_close` alanlarını ekleyin.
2. **İndikatör Hesabı:** `backtest.indicators.compute_indicators` fonksiyonu varsayılan olarak yerleşik (`builtin`) hesaplayıcıyı kullanır ve RSI, MACD, StochRSI gibi temel göstergeleri üretir. `pandas_ta` kütüphanesini kurup `engine="pandas_ta"` parametresini geçerseniz, kütüphane mevcutsa otomatik olarak kullanılacak; değilse yerleşik yöntemlere geri dönecektir.
3. **Filtreleme:** `backtest.screener.run_screener` fonksiyonunu kullanarak `filters.csv` içindeki sorguları çalıştırın. Varsayılan olarak eksik kolona sahip filtreler hata verir; filtreyi atlamak için `strict=False` parametresini kullanabilirsiniz. Filtre ifadelerinde kullanılabilen güvenli fonksiyonlar: `isin`, `notna`, `str`, `contains`, `abs`, `rolling`, `shift`, `mean`, `max`, `min`, `std`, `median`, `log`, `exp`, `floor`, `ceil`.
4. **Getiri Hesabı:** Filtre sonuçlarını `backtest.backtester.run_1g_returns` fonksiyonuna vererek T+N getirilerini hesaplayın. Tatil ve hafta sonu hatalarını önlemek için `trading_days` parametresine işlem günlerini geçin.
5. **Raporlama:** Çıktıları `backtest.reporter.write_reports` veya `backtest.report.write_report` aracılığıyla Excel/CSV olarak kaydedin.

## Sürüm Notları
- 1.2.0: spacy, fastai ve fastdownload bağımlılıkları kaldırıldı.
- 1.1.0: Colab desteği ve yeni README.
- 1.0.0: İlk yayımlanan sürüm.

