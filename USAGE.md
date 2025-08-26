# USAGE

## Kurulum

Geliştirme ortamı:

```bash
make dev-setup
```

Colab ortamı:

```python
!make colab
```

opencv gerekiyorsa:

```bash
pip install '.[cv]'
```

## Komut Listesi
| Komut | Açıklama | Önemli Argümanlar |
|-------|----------|-------------------|
| dry-run | filters.csv doğrulama | \-\-filters, --alias |
| scan-day | Tek gün tarama | --date, --data, \-\-filters |
| scan-range | Tarih aralığı tarama | --start, --end, --data |
| summarize | Sinyal özetleri ve BIST karşılaştırması | --data, --signals |
| report-excel | CSV özetlerinden Excel rapor | --daily, --filter-counts |
| portfolio-sim | Portföy simülasyonu | --portfolio, --costs |
| eval-metrics | Sinyal/portföy metrikleri | --start, --end |
| guardrails | Guardrail kontrolleri | --out-dir |
| config-validate | YAML config doğrulama | --config, --portfolio |
| compare-strategies | Strateji karşılaştırma | --start, --end, --space |
| tune-strategy | Tek strateji tuning | --start, --end, --space |
| convert-to-parquet | Excel'den Parquet üretimi | --excel-dir, --out |
| fetch-range | Veri aralığı indir | --symbols, --start, --end |
| fetch-latest | En son veriyi indir | --symbols, --ttl-hours |
| refresh-cache | Önbelleği yenile | --ttl-hours |
| vacuum-cache | Eski parçaları sil | --older-than-days |
| integrity-check | Parquet bütünlüğü kontrolü | --symbols |

## Filtre CSV formatı

`filters.csv` dosyası `FilterCode;PythonQuery` kolonlarından oluşur ve
ayraç olarak yalnızca noktalı virgül (`;`) kullanılabilir. Excel'den kaydederken
`CSV` biçiminde `;` ayırıcı seçilmelidir. Virgüllü dosyalar şu hatayı üretir:

```
CSV delimiter ';' bekleniyor. Dosyayı ';' ile kaydedin: FilterCode;PythonQuery
```

Eski virgüllü dosyaları dönüştürmek için `tools/migrate_filters_csv.py`
yardımcı programını kullanabilirsiniz.

`PythonQuery` boş bırakılamaz; boş veya sadece boşluk içeren satırlar
`ValueError` ile reddedilir.

## Filtre DSL Notu
Filtre ifadelerinde `cross_up(x,y)` ve `cross_down(x,y)` fonksiyonları
kullanılır. Yazımı farklı olsa bile (`CROSSUP`, `crossOver`, `keser_yukari`
vb.) ifadeler otomatik olarak bu kanonik küçük harf isimlere çevrilir.

## İsimlendirme Standardı
Tüm sütun ve gösterge adları **küçük harf + snake_case** biçimindedir.
Parametreler alt çizgi ile eklenir; ondalık değerler `.` yerine `p` ile
yazılır (`20.5` → `20p5`). Türkçe veya İngilizce eş anlamlı adlar tek
kanonik isme dönüştürülür (`hacim`, `islem_hacmi`, `lot` → `volume`).

| ham | kanonik |
| --- | --- |
| `SMA50` | `sma_50` |
| `BBU_20_2.0` | `bbu_20_2` |
| `hacim` | `volume` |
| `bbm_20.5_2` | `bbm_20p5_2` |

CSV dosyalarında kanonik isimleri kullanmanız önerilir; ancak ham girdiler
de desteklenir ve otomatik olarak normalize edilir.

## Filtre derleme
Programatik kullanımda filtre ifadelerini derlemek için
`backtest.filters_compile` modülü kullanılabilir. İki temel fonksiyon vardır:
`compile_expression` tek bir ifadeyi fonksiyona dönüştürür,
`compile_filters` ise bir ifade listesini derler.

```python
from backtest.filters_compile import compile_expression, compile_filters
import pandas as pd

df = pd.DataFrame({"a": [1, 2, 3], "b": [0, 1, 2]})
fn = compile_expression("cross_up(a,b)")
mask = fn(df)  # bool Series döner

funcs = compile_filters(["a > b", "b > a"])
```

## Komut Başına Rehber
### dry-run
**Amaç:** filters.csv dosyasının yapısını ve alias eşleşmelerini kontrol eder.

| Flag | Tip | Varsayılan | Açıklama |
|------|-----|------------|----------|
| \-\-filters | yol | zorunlu | Filtre dosyası |
| --alias | yol | `data/alias_mapping.csv` | Alias eşlemesi |

**Örnek**
```bash
python -m backtest.cli dry-run \-\-filters filters.csv
```

### scan-day
**Amaç:** Tek gün için filtre taraması çalıştırır.

| Flag | Tip | Varsayılan | Açıklama |
|------|-----|------------|----------|
| --date | YYYY-MM-DD | `None` | Hedef gün |
| --data | yol | `None` | Fiyat verisi (Excel/CSV/Parquet) |
| \-\-filters | yol | `None` | Filtre tanımları |
| --alias | yol | `data/alias_mapping.csv` | Alias eşlemesi |
| --out | yol | `None` | Çıktı dizini |
| \-\-filters-off | flag | `False` | Filtreleri devre dışı bırak |
| --no-write | flag | `False` | Dosya yazma |
| --costs | yol | `None` | Maliyet config |
| --report-alias | flag | `False` | Alias raporu |
| --no-preflight | flag | `False` | Ön kontrolü atla |

**Örnek**
```bash
python -m backtest.cli scan-day \
  --data data/BIST.xlsx \-\-filters filters.csv \
  --date 2024-01-02 --out raporlar/gunluk
```

### scan-range
**Amaç:** Tarih aralığı üzerinde tarama yapar.

| Flag | Tip | Varsayılan | Açıklama |
|------|-----|------------|----------|
| --start | YYYY-MM-DD | `None` | Başlangıç tarihi |
| --end | YYYY-MM-DD | `None` | Bitiş tarihi |
| --out | yol | `None` | Çıktı dizini |
| (diğerleri) | | | `scan-day` ile aynı |

**Örnek**
```bash
python -m backtest.cli scan-range \
  --data data/BIST.xlsx \-\-filters filters.csv \
  --start 2024-01-02 --end 2024-01-05
```

### summarize
**Amaç:** Günlük sinyallerden BIST karşılaştırmalı özet üretir.

| Flag | Tip | Varsayılan | Açıklama |
|------|-----|------------|----------|
| --data | yol | zorunlu | Fiyat paneli |
| --signals | yol | zorunlu | Günlük sinyal klasörü |
| --benchmark | yol | `data/BIST.xlsx` | BIST kapanış serisi |
| --out | yol | `raporlar/ozet` | Çıktı dizini |
| --horizon | int | `1` | Gün ufku |

**Örnek**
```bash
python -m backtest.cli summarize \
  --data data/panel.parquet --signals raporlar/gunluk
```

### report-excel
**Amaç:** CSV özetlerinden tek Excel raporu oluşturur.

| Flag | Tip | Varsayılan | Açıklama |
|------|-----|------------|----------|
| --daily | yol | zorunlu | daily_summary.csv |
| --filter-counts | yol | zorunlu | filter_counts.csv |
| --out | yol | `raporlar/ozet/summary.xlsx` | Çıktı dosyası |

**Örnek**
```bash
python -m backtest.cli report-excel \
  --daily raporlar/ozet/daily_summary.csv \
  --filter-counts raporlar/ozet/filter_counts.csv
```

### portfolio-sim
**Amaç:** Basit portföy simülasyonu yapar.

| Flag | Tip | Varsayılan | Açıklama |
|------|-----|------------|----------|
| --portfolio | yol | `config/portfolio.yaml` | Portföy ayarları |
| --costs | yol | `config/costs.yaml` | Maliyet ayarları |
| --risk | yol | `None` | Risk config |
| --start | YYYY-MM-DD | `None` | Başlangıç |
| --end | YYYY-MM-DD | `None` | Bitiş |

**Örnek**
```bash
python -m backtest.cli portfolio-sim \
  --portfolio config/portfolio.yaml \
  --start 2024-01-01 --end 2024-01-05
```

### eval-metrics
**Amaç:** Sinyal ve portföy metriklerini hesaplar.

| Flag | Tip | Varsayılan | Açıklama |
|------|-----|------------|----------|
| --start | YYYY-MM-DD | zorunlu | Başlangıç |
| --end | YYYY-MM-DD | zorunlu | Bitiş |
| --price-col | str | `close` | Fiyat kolonu |
| --horizon-days | int | `5` | Ufuk |
| --threshold-bps | float | `50` | Eşik |
| --signal-cols | liste | `entry_long` | Sinyal kolonları |
| --signals-csv | yol | `None` | Sinyal verisi |
| --equity-csv | yol | `artifacts/portfolio/daily_equity.csv` | Özkaynak |
| --weights-csv | yol | `artifacts/portfolio/weights.csv` | Ağırlıklar |

**Örnek**
```bash
python -m backtest.cli eval-metrics --start 2024-01-01 --end 2024-01-05
```

### guardrails
**Amaç:** Look-ahead gibi hataları yakalamak için kontrol çalıştırır.

| Flag | Tip | Varsayılan | Açıklama |
|------|-----|------------|----------|
| --out-dir | yol | `artifacts/guardrails` | Çıktı klasörü |

**Örnek**
```bash
python -m backtest.cli guardrails
```

### config-validate
**Amaç:** Config dosyalarını şema ile doğrular.

| Flag | Tip | Varsayılan | Açıklama |
|------|-----|------------|----------|
| --config | yol | `config/colab_config.yaml` | Ana config |
| --portfolio | yol | `config/portfolio.yaml` | Portföy config |
| --costs | yol | `config/costs.yaml` | Maliyet config |
| --export-json-schema | flag | `False` | Şema export |

**Örnek**
```bash
python -m backtest.cli config-validate
```

### compare-strategies
**Amaç:** Aynı veri üzerinde birden fazla stratejiyi koşturur.

| Flag | Tip | Varsayılan | Açıklama |
|------|-----|------------|----------|
| --start | YYYY-MM-DD | zorunlu | Başlangıç |
| --end | YYYY-MM-DD | zorunlu | Bitiş |
| --space | yol | zorunlu | Strateji tanımları |

**Örnek**
```bash
python -m backtest.cli compare-strategies \
  --start 2024-01-01 --end 2024-01-05 --space config/strategies.yaml
```

### tune-strategy
**Amaç:** Tek strateji için hiper-parametre araması yapar.

| Flag | Tip | Varsayılan | Açıklama |
|------|-----|------------|----------|
| --start | YYYY-MM-DD | zorunlu | Başlangıç |
| --end | YYYY-MM-DD | zorunlu | Bitiş |
| --space | yol | zorunlu | Arama uzayı |
| --cv | str | `walk-forward` | Çapraz doğrulama |
| --search | str | `grid` | Arama türü |
| --max-iters | int | `10` | Iterasyon |
| --seed | int | `None` | Rastgelelik |

**Örnek**
```bash
python -m backtest.cli tune-strategy \
  --start 2024-01-01 --end 2024-01-05 --space config/tune.yaml
```

### convert-to-parquet
**Amaç:** Excel kaynaklarından bölümlü Parquet üretir.

| Flag | Tip | Varsayılan | Açıklama |
|------|-----|------------|----------|
| --excel-dir | yol | `paths.EXCEL_DIR` | Excel kaynak klasörü |
| --out | yol | zorunlu | Parquet çıkışı |

**Örnek**
```bash
python -m backtest.cli convert-to-parquet --out data/parquet
```

### fetch-range
**Amaç:** Belirli tarih aralığı için veri indirir.

| Flag | Tip | Varsayılan | Açıklama |
|------|-----|------------|----------|
| --symbols | liste | zorunlu | Semboller (virgül ile ayrılmış) |
| --start | YYYY-MM-DD | zorunlu | Başlangıç |
| --end | YYYY-MM-DD | zorunlu | Bitiş |
| --provider | str | `stub` | Sağlayıcı |
| --directory | yol | `data/` | Çıktı dizini |

**Örnek**
```bash
python -m backtest.cli fetch-range \
  --symbols DEMO --start 2024-01-01 --end 2024-01-05
```

### fetch-latest
**Amaç:** TTL'e göre en güncel veriyi indirir.

| Flag | Tip | Varsayılan | Açıklama |
|------|-----|------------|----------|
| --symbols | liste | zorunlu | Semboller |
| --ttl-hours | int | `6` | Geçerlilik süresi |
| --provider | str | `stub` | Sağlayıcı |
| --directory | yol | `data/` | Çıktı dizini |

**Örnek**
```bash
python -m backtest.cli fetch-latest --symbols DEMO
```

### refresh-cache
**Amaç:** Önbellekteki verileri günceller.

| Flag | Tip | Varsayılan | Açıklama |
|------|-----|------------|----------|
| --ttl-hours | int | `0` | Yenileme eşiği |
| --provider | str | `stub` | Sağlayıcı |
| --directory | yol | `data/` | Çıktı dizini |

**Örnek**
```bash
python -m backtest.cli refresh-cache
```

### vacuum-cache
**Amaç:** Eski parçaları temizler.

| Flag | Tip | Varsayılan | Açıklama |
|------|-----|------------|----------|
| --older-than-days | int | `365` | Yaş eşiği |
| --provider | str | `stub` | Sağlayıcı |
| --directory | yol | `data/` | Çıktı dizini |

**Örnek**
```bash
python -m backtest.cli vacuum-cache
```

### integrity-check
**Amaç:** Parquet parçalarının bütünlüğünü kontrol eder.

| Flag | Tip | Varsayılan | Açıklama |
|------|-----|------------|----------|
| --symbols | liste | zorunlu | Semboller |
| --provider | str | `stub` | Sağlayıcı |
| --directory | yol | `data/` | Çıktı dizini |

**Örnek**
```bash
python -m backtest.cli integrity-check --symbols DEMO
```

## Veri Yolu & ENV
- `DATA_DIR`: Tüm verilerin kökü (`data/`).
- `EXCEL_DIR`: Excel kaynak klasörü; varsayılan `DATA_DIR`.
## Sık Karşılaşılan Hatalar
- Yol bulunamadı: `filters.csv` veya veri dosyaları için tam yol belirtin.
- İzin reddedildi: İlgili dizinlerin yazma izni olduğundan emin olun.
- Eksik argüman: CLI yardımını `-h` ile kontrol edin.
 Daha fazla bilgi için [TROUBLESHOOT.md](TROUBLESHOOT.md) dosyasına bakın.

## Ekler / İpuçları
- Loglar varsayılan olarak `loglar/` klasörüne, artefaktlar `artifacts/`
  altına yazılır.
- Platformlar arası çalışırken Windows yol ayracı için çift ters bölü (
  `\\`) kullanın.
