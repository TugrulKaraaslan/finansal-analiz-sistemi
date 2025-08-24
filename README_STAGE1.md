# README Stage 1

## Proje Özeti
Bu depo, finansal zaman serileri için temel tarama ve raporlama araçları
sunar. Varsayılan tek veri kaynağı `data/` dizinidir ve tüm yol çözümleri
`backtest/paths.py` içinden yapılır. Çevrimdışı çalışma varsayılandır;
indirme işlemleri yalnızca manuel bayrak veya ortam değişkeni ile
etkinleştirilebilir.

## Kurulum
- Python ≥3.10, <3.13 gerektirir.
- Sanal ortam oluşturun ve bağımlılıkları yükleyin:

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

İsteğe bağlı olarak proje kökünde düzenlenebilir kurulum yapabilirsiniz:

```bash
pip install -e .
```

## Veri Dizini
Tek veri yolu `data/` altındadır. Örnek dosyalar:
- `data/BIST.xlsx`
- `data/alias_mapping.csv`

Varsayılan yollar ortam değişkenleri ile değiştirilebilir:
- `DATA_DIR` tüm verilerin temel dizinidir.
- `EXCEL_DIR` Excel kaynaklarını gösterir; verilmezse `DATA_DIR`
  kullanılır.

Örnek override:

```bash
DATA_DIR=/mnt/veri EXCEL_DIR=/mnt/excel \
python -m backtest.cli convert-to-parquet --out /tmp/parquet
```

## Filtre DSL Notu
Filtre ifadelerinde `cross_up(x,y)` ve `cross_down(x,y)` isimli küçük harf
fonksiyonları kullanılır. `CROSSUP`, `CROSSDOWN`, `crossOver`, `crossUnder`
ve Türkçe varyantlar gibi farklı yazımlar otomatik olarak bu kanonik
fonksiyonlara dönüştürülür.

## Hızlı Başlangıç
Aşağıdaki komutlar örnek verilerle çevrimdışı çalışır.

```bash
# filters.csv dosyasını doğrula
python -m backtest.cli dry-run --filters filters.csv

# Excel dosyalarını Parquet'e çevir
python -m backtest.cli convert-to-parquet --out data/parquet

# Tek gün tarama yap
python -m backtest.cli scan-day \
  --data data/BIST.xlsx --filters filters.csv \
  --date 2024-01-02 --out raporlar/gunluk
```

## Offline Varsayılanı
Harici indirme kapalıdır. İndirme yapmak için
`--allow-download` bayrağı veya `ALLOW_DOWNLOAD=1` ortam değişkeni
kullanılmalıdır.

## Sorun Giderme & Detaylı Kullanım
Ek argümanlar, tüm alt komutlar ve ipuçları için
[`USAGE.md`](USAGE.md) dosyasına bakın.
