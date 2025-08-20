# Finansal Analiz Sistemi

Bu proje, BIST verileri üzerinde filtre bazlı tarama yaparak raporlar üretir.

## Hızlı Başlangıç (Lokal)

```bash
python -m venv .venv && source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
make colab-setup
python -m backtest.cli --help
```

## Testleri Çalıştırma

```bash
make tests
```

## Veri ve Filtre Dosyaları

* **Excel klasörü**: `Veri/` (proje kökünde)
* **filters.csv**: proje kökünde, ayracı `;`, başlıklar: `FilterCode;PythonQuery`

Örnek ilk satır:

```
FilterCode;PythonQuery
EXAMPLE_01; (rsi_14 > 50) & (ema_20 > ema_50)
```

## Config Dosyası

Varsayılan örnek: `config/colab_config.yaml.example` (aşağıda). Kendi çalıştırman için bunu `config/colab_config.yaml` olarak kopyala ve tarihleri düzenle.

## Benchmark (opsiyonel)

Benchmarkt kaynağı config'te şu şekilde tanımlanır:

```yaml
benchmark:
  source: "excel"
  excel_path: "/content/finansal-analiz-sistemi/Veri/BIST.xlsx"
  excel_sheet: "BIST"
  column_date: "date"
  column_close: "close"
```

Komut örneği:

```bash
python -m backtest.cli scan-day --config config/colab_config.yaml --date 2025-03-07
```

## CLI Kullanımı (tek doğru biçim)

```bash
# Tek gün
python -m backtest.cli scan-day --config config/colab_config.yaml --date 2025-03-07

# Tarih aralığı
python -m backtest.cli scan-range --config config/colab_config.yaml --start 2022-01-03 --end 2025-04-18
```

> `--config` opsiyoneldir (varsayılan: `config_scan.yml`). Pozisyonel argüman **DEĞİLDİR**.

## Yol Öncelik Sırası

`--config` ve `--filters-csv` gibi yol argümanları şu öncelik sırasıyla değerlendirilir:

1. CLI argümanı
2. YAML config içeriği
3. Kod içi varsayılan (`config_scan.yml`, `filters.csv`)

Hem mutlak hem göreli yollar desteklenir ve dahili olarak `Path(...).expanduser().resolve()` ile gerçek yola çevrilir.

```bash
python -m backtest.cli scan-range --filters-csv my/filters.csv
```
Yukarıdaki komutta `my/filters.csv` kullanılır; YAML veya varsayılan yol yok sayılır.

## Test ve Preflight Kontrolü

Kod değişikliklerinden sonra hızlı bir kontrol için aşağıdaki testi çalıştır:

```bash
pytest tests/smoke/test_loader_and_preflight.py -q
pytest tests/e2e/test_scan_range.py -q
pytest tests/smoke/test_cli_entrypoints.py -q
```

Preflight doğrulamasını atlamak için CLI'da `--no-preflight` bayrağını veya
config dosyasında `preflight: false` ayarını kullanabilirsin:

```bash
python -m backtest.cli scan-range \
  --config config_scan.yml \
  --no-preflight \
  --start 2024-01-02 --end 2024-01-05
```

## Filtre Alias Raporu

Filtre dosyasını temizlemek ve alias uyumsuzluklarını raporlamak için yeni bayraklar kullanılır:

```bash
python -m backtest.cli scan-range --config config_scan.yml \
  --no-preflight --report-alias \
  --filters-csv config/filters.csv \
  --reports-dir raporlar/
```

Örnek tarama çok-gün bir Excel üzerinde çalışır, isteğe bağlı olarak preflight
kontrolü atlanabilir ve `alias_uyumsuzluklar.csv` dosyasına alias raporu yazılır.

## Rapor ve Log Dizini

Komutlar çalıştığında çıktı dosyaları `raporlar/` klasörüne, loglar ise her çalıştırma için ayrı bir alt klasör oluşturularak `loglar/` içine yazılır.

```
raporlar/
    SCAN_2025-03-07.xlsx
loglar/
    run_20250101-120000/
        summary.txt
        stages.jsonl
```

Colab veya uzak bir ortamda sonuçları indirmenin kolay yolu:

```bash
zip -r raporlar.zip raporlar
zip -r loglar.zip loglar
zip -r reports_logs.zip raporlar loglar  # ikisi birden
```

Bu dosyaları `drive.mount` ile Google Drive'a kopyalayabilir veya tarayıcıdan indirebilirsin.

## Sık Karşılaşılan Hatalar

* **ModuleNotFoundError: pandera/loguru** → `pip install -r requirements.txt`
* **Excel klasörü bulunamadı** → `excel_dir` **mutlak** olsun ya da göreli ise **proje köküne göre** çözümlenir (aşağıdaki kod bu hatayı bitirir).
* **Colab kurulum uyarıları** → Colab’da paket sürümü değiştiyse **Runtime → Restart runtime** ve **requirements kurulumu** sonrası devam.

Colab için ayrıntılar: `docs/colab.md`.

