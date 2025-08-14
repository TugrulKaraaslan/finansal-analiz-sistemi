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

## İsimlendirme Standardı
Tüm iç kolon ve alan adları `snake_case` biçiminde tutulur: yalnızca küçük
harf, rakam ve altçizgi (`[a-z0-9_]+`). Örnek kanonik adlar: `open`, `high`,
`low`, `close`, `volume`, `ema_20`, `rsi_14`.

## Alias Davranışı
Eski veya farklı yazımlara ait varyasyonlar geniş bir eşleme tablosu ile
kanonik adlara dönüştürülür. Pandera tabanlı `validate_columns_schema`
yardımıyla iki çalışma modu bulunur:

- **`strict_fail`**: eşleşmeyen kolonlar hata olarak raporlanır.
- **`auto_fix`**: bilinen alias'lar düzeltilir, tanınmayanlar atlanarak
  döndürülen listede bildirilir.

Filtre ifadeleri de aynı normalizasyon katmanından geçtiği için sorgularda
`EMA20` yazmak `ema_20` kolonunu kullanır.

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

## BIST'e Göre Oranlı Özet

Filtre performansları BIST100'e göre şu metriklerle özetlenir:

| FİLTRE | MEAN_RET | BIST_MEAN_RET | ALPHA_RET | HIT_RATIO | N_TRADES |
| -----: | --------: | --------------: | ---------: | ---------: | --------: |
|    T21 |    0.0124 |          0.0080 |     0.0044 |       0.61 |        57 |
|    T24 |    0.0102 |          0.0091 |     0.0011 |       0.54 |        49 |

`ALPHA_RET = MEAN_RET - BIST_MEAN_RET`

## Kurulum ve Çalıştırma
### Yerel
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt -c constraints.txt --only-binary=:all: --no-binary=pandas-ta
pip install -r requirements_dev.txt -c constraints.txt --only-binary=:all: --no-binary=pandas-ta  # test/geliştirici ortamı
```

#### Ortam Doğrulama

```python
!python tools/verify_env.py
```

Python 3.10–3.12 sürümleri desteklenir; 3.13 henüz destek dışıdır.

Excel dosyalarını okuyup yazmak için gerekli `openpyxl` ve `XlsxWriter` paketleri de bu gereksinimlerle kurulur.

Spacy, fastai ve fastdownload bağımlılıkları kaldırılmış olup kurulmasına gerek yoktur.

```bash
python -m backtest.cli scan-day --config examples/example_config.yaml --date 2024-01-02
```
### Google Colab
```python
!pip install -q -r requirements_colab.txt -c constraints.txt --only-binary=:all:
!python tools/verify_env.py
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

## Log Standardı

Varsayılan log dizini `loglar/` olarak belirlenmiştir. Her çalışma
`run_YYYYMMDD-HHMMSS` şeklinde adlandırılan alt klasöre loglarını yazar:

```
loglar/
  run_20250307-093015/
    summary.txt
    stages.jsonl
```

`summary.txt` kısa insan okunur özetler içerir. Ayrıntılı bilgiler ise
JSON Lines biçimindeki `stages.jsonl` dosyasına yazılır:

```json
{"ts":"2025-03-07T09:30:15.120Z","stage":"load_data","elapsed_ms":215,"rows":48290}
```

Hatalar `ERROR` seviyesinde loglanır ve aynı klasörde `stage.err` olarak
stacktrace ile saklanır. Önceki `logs/` dizini tespit edilirse köke
`migration.txt` bırakılır ve konsola uyarı basılır.

`purge_old_logs(days=7)` fonksiyonu çalıştırıldığında 7 günden eski
`run_*` klasörleri otomatik olarak silinir.

### Gösterge Motoru (Politika Kilidi)

- Sistem hiçbir koşulda gösterge hesaplamaz; tüm indikatör kolonları veriyle
  birlikte gelmelidir.
- `compute_indicators` fonksiyonu yalnızca gelen DataFrame'i aynen döndürür ve
  bilgi amaçlı şu satırı loglar:

  ```
  indicators: engine=none (policy lock), no computation
  ```

- Daha önce `pandas_ta` gibi kütüphanelerle yapılan hesaplamalar artık desteklenmez;
  göstergeleri veri hazırlama hattında üretmeniz gerekir.

### Hazır Gösterge Kolonları ve Kesişimler

- Kesişim alanları mevcut kolonlardan üretilir; yeniden hesaplama yapılmaz.
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

Gün başına Excel (ve varsayılan olarak CSV) üretmek için:

```bash
python -m backtest.cli scan-range \
  --config examples/example_config.yaml \
  --start 2025-03-07 \
  --end   2025-03-11 \
  --per-day-output
```

CSV istemiyorsanız `--no-csv` bayrağını ekleyin.

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

## Ön Kontrol (Preflight)

Tarama başlamadan önce belirtilen klasör ve tarih aralığı için dosya varlığı
kontrol edilir. Eksik dosyalar raporlanır ve sık yapılan hatalar için öneriler
sunulur. Gerekirse `--no-preflight` ile kontrolü atlayabilir ya da
`--case-insensitive` bayrağıyla dosya adlarında küçük/büyük harf farkını yok
sayabilirsiniz.

Örnek çıktı:

```
preflight: scanned=4, found=3, missing=1, dir=Veri, pattern={date}.xlsx
Eksik dosyalar: 2025-03-10
Öneri: Klasörü 'veri/' altında buldum. Config'te 'excel_dir: veri' yapmayı dener misin?
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
2. **Gösterge Adımı:** `backtest.indicators.compute_indicators` artık hiçbir hesaplama yapmaz;
   verideki hazır indikatör kolonları aynen korunur.
3. **Filtreleme:** `backtest.screener.run_screener` fonksiyonunu kullanarak `filters.csv` içindeki sorguları çalıştırın. Varsayılan olarak eksik kolona sahip filtreler atlanır; hatada durmak için `stop_on_filter_error=True` parametresini kullanabilirsiniz. Filtre ifadelerinde kullanılabilen güvenli fonksiyonlar: `isin`, `notna`, `str`, `contains`, `abs`, `rolling`, `shift`, `mean`, `max`, `min`, `std`, `median`, `log`, `exp`, `floor`, `ceil`.
4. **Getiri Hesabı:** Filtre sonuçlarını `backtest.backtester.run_1g_returns` fonksiyonuna vererek T+N getirilerini hesaplayın. Tatil ve hafta sonu hatalarını önlemek için `trading_days` parametresine işlem günlerini geçin.
5. **Raporlama:** Çıktıları `backtest.reporter.write_reports` veya `backtest.report.write_report` aracılığıyla Excel/CSV olarak kaydedin.

## Sürüm Notları
- 1.2.0: spacy, fastai ve fastdownload bağımlılıkları kaldırıldı.
- 1.1.0: Colab desteği ve yeni README.
- 1.0.0: İlk yayımlanan sürüm.

