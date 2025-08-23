# Finansal Analiz Sistemi

Bu proje, BIST verileri üzerinde filtre bazlı tarama yaparak raporlar üretir.

Kullanım için [USAGE.md](USAGE.md), sık sorular için [FAQ.md](FAQ.md) ve hata çözümü için [TROUBLESHOOT.md](TROUBLESHOOT.md) dosyalarına bakın.

## Hızlı Başlangıç (Lokal)

```bash
python -m venv .venv && source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
pip install -r requirements-dev.txt
python -m backtest.cli --help
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

## Veri ve Filtre Dosyaları

* **Excel klasörü**: `Veri/` (proje kökünde)
* **filters.csv**: proje kökünde, ayracı `;`, başlıklar: `FilterCode;PythonQuery`

Örnek satırlar:

```
FilterCode;PythonQuery
EX1; ichimoku_conversionline > ichimoku_baseline
EX2; macd_line > macd_signal
```

Excel klasör yolu config dosyasından okunur; CLI'da `--excel-dir` parametresi bulunmaz.

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
python -m backtest.cli scan-range --config config/colab_config.yaml --start 2025-03-07 --end 2025-03-11
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

Preflight doğrulaması varsayılan olarak açıktır. İstersen CLI'da `--no-preflight`
bayrağını veya config dosyasında `preflight: false` ayarını kullanabilirsin:

```bash
python -m backtest.cli scan-range \
  --config config_scan.yml \
  --no-preflight \
  --start 2024-01-02 --end 2024-01-05
```

## Filtre İfadeleri ve Alias'lar

 Filtre motoru DataFrame kolonlarını bire bir kullanır ve her kolonun
 lower-case kopyasını otomatik olarak sağlar. Legacy isimler için aşağıdaki
 alias haritası tanımlıdır. Preflight aşamasında alias kullanımı varsayılan
 olarak **hatadır**. Lokal geliştirmede geçici olarak izin vermek için CLI'da
 `--allow-alias` bayrağı veya YAML config'te `allow_alias: true` anahtarı
 kullanılabilir. CI'da bu seçenekler geçersizdir; alias'lar mutlaka
 kanonik isimlere dönüştürülmelidir:

Detaylar için [docs/ALIAS_POLICY.md](docs/ALIAS_POLICY.md) ve kanonik kolon listesi için [docs/canonical_names.md](docs/canonical_names.md) dosyalarına bakın.

* `its_9` → `ichimoku_conversionline`
* `iks_26` → `ichimoku_baseline`
* `macd_12_26_9` → `macd_line`
* `macds_12_26_9` → `macd_signal`
* `bbm_20 2` → `bbm_20_2` (benzer şekilde `bbu_20 2` ve `bbl_20 2`)

Alias içeren dosyaları kanonik hale getirmek için `tools/canonicalize_filters.py`
aracını kullanabilirsiniz.

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

## Filtre Kanonikleştirme Aracı

`filters.csv` içindeki legacy alias'ları kanonik isimlere dönüştürmek için:

```bash
python tools/canonicalize_filters.py filters.csv filters_canonical.csv
```

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

