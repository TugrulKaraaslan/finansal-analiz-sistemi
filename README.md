# Finansal Analiz Sistemi

Bu proje, BIST verileri üzerinde filtre bazlı tarama yaparak raporlar üretir.

## Hızlı Başlangıç (Lokal)

```bash
python -m venv .venv && source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
python -m backtest.cli --help
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

## CLI Kullanımı (tek doğru biçim)

```bash
# Tek gün
python -m backtest.cli scan-day --config config/colab_config.yaml --date 2025-03-07

# Tarih aralığı
python -m backtest.cli scan-range --config config/colab_config.yaml --start 2022-01-03 --end 2025-04-18
```

> `--config` **zorunludur**. Pozisyonel argüman **DEĞİLDİR**.

## Sık Karşılaşılan Hatalar

* **ModuleNotFoundError: pandera/loguru** → `pip install -r requirements.txt`
* **Excel klasörü bulunamadı** → `excel_dir` **mutlak** olsun ya da göreli ise **proje köküne göre** çözümlenir (aşağıdaki kod bu hatayı bitirir).
* **Colab kurulum uyarıları** → Colab’da paket sürümü değiştiyse **Runtime → Restart runtime** ve **requirements kurulumu** sonrası devam.

Colab için ayrıntılar: `docs/colab.md`.

