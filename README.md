# Finansal Analiz Sistemi

![tests](https://img.shields.io/github/actions/workflow/status/TugrulKaraaslan/finansal-analiz-sistemi/ci.yml?branch=main)
![python](https://img.shields.io/badge/python-3.11-blue)
![release](https://img.shields.io/badge/release-A12-success)

Bu proje, BIST verileri üzerinde filtre bazlı tarama yaparak raporlar üretir.
> Migration notu: CSV desteği kaldırıldı; modül bazlı sisteme geçildi.
Son sürüm: [A12](CHANGELOG.md#A12--2025-08-23) (2025-08-23).

Kullanım için [USAGE.md](USAGE.md), sık sorular için [FAQ.md](FAQ.md) ve hata çözümü için [TROUBLESHOOT.md](TROUBLESHOOT.md) dosyalarına bakın.

## Hızlı Başlangıç (Lokal)

```bash
python -m venv .venv && source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
pip install -r requirements-dev.txt
python -m backtest.cli --help
```

Tek veri kaynağı depo kökündeki `data/` dizinidir.


## CLI Örnekleri

```bash
# Tek gün taraması
python -m backtest.cli --log-level INFO --json-logs scan-day \
  --data data/BIST.parquet \
  --filters-module io_filters --filters-include "*" \
  --date 2024-01-02 --reports-dir raporlar/gunluk

# Tarih aralığı taraması
python -m backtest.cli --log-level INFO --json-logs scan-range \
  --data data/BIST.parquet \
  --filters-module io_filters --filters-include "*" \
  --start 2024-01-02 --end 2024-01-05 --reports-dir raporlar/aralik

# Config üzerinden filtre override
python -m backtest.cli scan-day --config config/scan.yml \
       --filters-module io_filters --filters-include "*"
```


## Hızlı Başlangıç (Colab)

```python
!python notebooks/00_colab_bootstrap.py
```


## Testler Nasıl Çalıştırılır?

```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt
make fixtures
make preflight
make test
# Golden güncelleme gerektiğinde:
make golden
# Hepsini bir arada çalıştırmak için:
make check
```

## Konfig Şeması & Doğrulama

```bash
# Doğrulama + JSON Schema üretimi
make config-validate
# Çıkış: artifacts/schema/*.schema.json
```

## Log Ayarları

- `LOG_LEVEL` = DEBUG|INFO|WARNING|ERROR (default: INFO)
- `LOG_FORMAT` = json|plain (default: json)
- `LOG_DIR` = loglar (default)
- `BACKTEST_RUN_ID` = aynı koşudaki tüm logları korele etmek için custom run id
- CLI global bayrakları: `--log-level` ve `--json-logs`

```bash
LOG_LEVEL=DEBUG BACKTEST_RUN_ID=A12-DEV1 \
python -m backtest.cli scan-range --config config/colab_config.yaml --start 2025-03-07 --end 2025-03-09
```

## Performance

```bash
# micro benchmarks
make bench
# CLI smoke bench
make bench-cli
# CPU profile (HTML rapor → artifacts/profiles/...)
make profile
# Memory snapshot (JSON)
make mem
```

## Sonuç Dashboard’u

```bash
make report
# Çıktı: artifacts/report/index.html (yerelde dosyayı tarayıcıda aç)
```

CI koşuları sonunda rapor `html-report` artefaktı olarak yüklenir; Actions sekmesinden indirip `index.html` dosyasını açabilirsiniz.

## Günlük Artırımlı Çalıştırıcı

```bash
# Yerelde dünü çalıştır
make daily
# Başka günler için
DAYS_BACK=2 make daily
```

CI kullanımı:
- Settings → Secrets → Actions altına `DAILY_WEBHOOK_URL` (opsiyonel) ekle.
- Actions sekmesinden `daily` workflow'unu **Run workflow** ile manuel tetikleyebilir, `days_back` girebilirsin.


## Walk-Forward / Time-Series CV

```bash
# Varsayılan kısa smoke
make walk-forward

# Parametrelerle
WF_START=2025-03-01 \
WF_END=2025-03-31 \
WF_TRAIN_DAYS=10 \
WF_TEST_DAYS=2 \
WF_STEP_DAYS=2 \
make walk-forward
```

Tasarım notu: Bu PR yalnız iskelet sağlar; metrik/portföy sonuçlarını toplama PR-13’te detaylandırılır.

## Değerlendirme Metrikleri

```bash
# Sinyal + portföy metrikleri (mevcut artefaktları kullanarak)
python -m backtest.cli eval-metrics --start 2025-03-07 --end 2025-03-11 \
  --horizon-days 5 --threshold-bps 50 --signal-cols entry_long exit_long

# Çıktılar: signal_metrics.json, portfolio_metrics.json ve risk_metrics.json
# (Sharpe, Sortino, MaxDD, Turnover)
tree artifacts/metrics
```

## Guardrails

Tarama hattında look-ahead hatalarını önlemek için temel kontroller mevcuttur:

- Emirler varsayılan olarak **T+1** açılışında yürütülür.
- İlk `warmup_min_bars` süresince üretilen sinyaller geçersiz sayılır.
- DSL ifadelerinde `shift(-1)`, `lead(`, `next_` gibi geleceğe dönük desenler reddedilir.

Kontrolleri çalıştırmak için:

```bash
python -m backtest.cli guardrails
```

Çıktılar `artifacts/guardrails/` altında `summary.json` ve `violations.csv` dosyalarına yazılır.

## Portfolio Engine

Portföy motoru, sinyallerden gelen giriş/çıkışlara göre pozisyon boyutlarını hesaplar ve temel limitleri uygular. Üç farklı boyutlama modu desteklenir:

- `risk_per_trade`: ATR tabanlı veya yüzdesel stop mesafesi ile özsermayenin belirli bir bps'i riske atılır.
- `fixed_fraction`: Özsermayenin sabit bir yüzdesi pozisyona ayrılır.
- `target_weight`: Sinyal hedef ağırlık belirtiyorsa doğrudan notional hesaplanır.

`config/portfolio.yaml` içindeki limitler (max_positions, max_position_pct, max_gross_exposure, lot_size vb.) kontrol edilir. `config/costs.yaml` mevcutsa maliyetler `apply_costs` ile işlemlere eklenir.

CLI'dan basit bir simülasyon örneği:

```bash
python -m backtest.cli portfolio-sim --config config/colab_config.yaml --portfolio config/portfolio.yaml --start 2025-03-07 --end 2025-03-09
```

Çıktılar `artifacts/portfolio/` altında `trades.csv` ve `daily_equity.csv` olarak yazılır.

## Golden Güncelleme

```bash
# İlk kurulum (bir kere)
pip install -r requirements-dev.txt
pre-commit install

# Manuel güncelleme
make golden

# CI’de hata aldıysanız (out-of-date)
make golden && git add tests/golden/checksums.json && git commit -m "update golden checksums"
```

## Veri Kalitesi Sözleşmeleri

```bash
# Sözleşme kontrolü (lokalde)
make quality
# Rapor → artifacts/quality/report.json
```

Kurallar ve tolerans değerleri `contracts/data_quality.yaml` dosyasından
güncellenebilir. Şema ihlalleri ve mantıksal hatalar kritik kabul edilir ve
araç çıkış kodunu sıfırdan farklı yapar; tolerans aşımı uyarı olarak raporlanır.

## Config Dosyası

Varsayılan örnek: `config/colab_config.yaml.example` (aşağıda). Kendi çalıştırman için bunu `config/colab_config.yaml` olarak kopyala ve tarihleri düzenle.

## Benchmark (opsiyonel)

Benchmarkt kaynağı config'te şu şekilde tanımlanır:

```yaml
benchmark:
  source: "excel"
  excel_path: "data/BIST.xlsx"
  excel_sheet: "BIST"
  column_date: "date"
  column_close: "close"
```

Komut örneği:

```bash
python -m backtest.cli scan-day --config config/colab_config.yaml --date 2025-03-07
```

## Kendi filtre modülünü yaz

En küçük modül iki yöntemle tanımlanabilir:

```python
# my_filters.py
FILTERS = [
    {"FilterCode": "FI", "PythonQuery": "df['close'] > df['ema20']"},
    {"FilterCode": "RSI", "PythonQuery": "df['rsi14'] < 30"},
]
```

Alternatif olarak:

```python
# my_filters.py
def get_filters():
    return [
        {"FilterCode": "FI", "PythonQuery": "df['close'] > df['ema20']"},
        {"FilterCode": "RSI", "PythonQuery": "df['rsi14'] < 30"},
    ]
```

Konfig bağlama:

```yaml
filters:
  module: "my_filters"      # my_filters.py dosyanız
  include: ["FI","RSI*"]    # fnmatch desenleri
```

Çalıştırma:

```bash
python -m backtest.cli scan-day --config config/scan.yml \
       --filters-module my_filters --filters-include "FI" --filters-include "RSI*"
```

Hata ipuçları:

- `filters module missing FILTERS/get_filters` → modülünüzde yukarıdaki yapılardan biri yok.
- Include boş ise: filtreler devre dışı kalır (bilerek).

## CLI Kullanımı (tek doğru biçim)

```bash
# Tek gün
python -m backtest.cli scan-day --config config/colab_config.yaml --date 2025-03-07

# Tarih aralığı
python -m backtest.cli scan-range --config config/colab_config.yaml --start 2025-03-07 --end 2025-03-11
```

> `--config` opsiyoneldir (varsayılan: `config_scan.yml`). Pozisyonel argüman **DEĞİLDİR**.

## Yol Öncelik Sırası

`--config` gibi yol argümanları şu öncelik sırasıyla değerlendirilir:

1. CLI argümanı
2. YAML config içeriği
3. Kod içi varsayılan (`config_scan.yml`)

Hem mutlak hem göreli yollar desteklenir ve dahili olarak `Path(...).expanduser().resolve()` ile gerçek yola çevrilir.

## Test ve Preflight Kontrolü

Kod değişikliklerinden sonra hızlı bir kontrol için aşağıdaki testi çalıştır:

```bash
pytest tests/smoke/test_loader_and_preflight.py -q
pytest tests/e2e/test_scan_range.py -q
pytest tests/smoke/test_cli_entrypoints.py -q
```

Preflight doğrulaması varsayılan olarak açıktır. İstersen CLI'da `--no-preflight`
bayrağını veya config dosyasında `preflight: false` ayarını kullanabilirsin:

```bash
python -m backtest.cli scan-range \
  --config config_scan.yml \
  --no-preflight \
  --start 2024-01-02 --end 2024-01-05
```

## Filtre İfadeleri

Filtre motoru DataFrame kolonlarını bire bir kullanır ve her kolonun
lower-case kopyasını otomatik olarak sağlar. Çalışma zamanı **yalnızca
kanonik** isimleri kabul eder; tanımsız veya alias kolonlar preflight
sırasında **hata** üretir.
Kanonik kolon listesi için [docs/canonical_names.md](docs/canonical_names.md)
dosyasına bakabilirsiniz.

## Rapor ve Log Dizini

 Komutlar çalıştığında çıktı dosyaları `raporlar/` klasörüne, loglar ise her çalıştırma için ayrı bir alt klasör oluşturularak `loglar/` içine yazılır; her `run_*/` klasöründe `summary.txt` ve makine okunabilir `events.jsonl` bulunur.

```
raporlar/
    SCAN_2025-03-07.xlsx
loglar/
    run_20250101-120000/
        summary.txt
        events.jsonl
```

Colab veya uzak bir ortamda sonuçları indirmenin kolay yolu:

```bash
zip -r raporlar.zip raporlar
zip -r loglar.zip loglar
zip -r reports_logs.zip raporlar loglar  # ikisi birden
```

Bu dosyaları `drive.mount` ile Google Drive'a kopyalayabilir veya tarayıcıdan indirebilirsin.

## İşlem Maliyeti & Slippage

İşlem maliyetlerini simüle etmek için `config/costs.yaml` dosyası kullanılır. Varsayılan yapı:

```yaml
enabled: true
currency: TRY
rounding:
  cash_decimals: 2
commission:
  model: fixed_bps
  bps: 5
  min_cash: 0.0
taxes:
  bps: 0
spread:
  model: half_spread
  default_spread_bps: 7
slippage:
  model: atr_linear
  bps_per_1x_atr: 10
apply:
  price_col: fill_price
  qty_col: quantity
  side_col: side
  date_col: date
  id_col: trade_id
report:
  write_breakdown: true
  output_dir: artifacts/costs
```

Komisyon modelleri: `fixed_bps`, `per_share_flat`, `none`.
Spread modelleri: `half_spread`, `fixed_bps`, `none`.
Slippage modelleri: `atr_linear`, `fixed_bps`, `none`.

Maliyetler `trade` tablosuna uygulanır ve `cost_commission`, `cost_slippage`, `cost_taxes`, `cost_total` kolonları eklenir.

### Örnek kullanım

```bash
# Varsayılan maliyetlerle
python -m backtest.cli scan-range --config config/colab_config.yaml --start 2025-03-07 --end 2025-03-09

# Özel maliyet dosyasıyla
python -m backtest.cli scan-range --config config/colab_config.yaml --start 2025-03-07 --end 2025-03-09 --costs my_costs.yaml
```

## Sık Karşılaşılan Hatalar

* **ModuleNotFoundError: pandera/loguru** → `pip install -r requirements.txt`
* **Excel klasörü bulunamadı** → `excel_dir` **mutlak** olsun ya da göreli ise **proje köküne göre** çözümlenir (aşağıdaki kod bu hatayı bitirir).
* **Colab kurulum uyarıları** → Colab’da paket sürümü değiştiyse **Runtime → Restart runtime** ve **requirements kurulumu** sonrası devam.

Colab için ayrıntılar: `docs/colab.md`.

## Legacy conversion

Tek seferlik dönüştürücü ile eski CSV tabanlı filtreleri Python `FILTERS` modülüne çevirebilirsin:

```bash
python tools/legacy/migrate_filters_csv.py legacy_filters_file.csv FILTERS.py
```

Normal koşularda CSV filtre desteği yoktur; yalnızca geçmiş veriyi taşımak için kullan.

## Contributing

CSV/legacy flag'ler CI’da fail eder; tools/legacy/** altı hariç.

