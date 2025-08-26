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

## İsimlendirme Standardı
Tüm gösterge ve sütun adları **küçük harf + snake_case** formatındadır.
Parametreler alt çizgi ile ayrılır; ondalık parametreler `p` ile
yazılır (`20.5` → `20p5`). Türkçe/İngilizce eş anlamlılar tek kanonik isme
dönüşür (`hacim`, `islem_hacmi`, `lot` → `volume`).

| ham | kanonik |
| --- | --- |
| `SMA50` | `sma_50` |
| `BBU_20_2.0` | `bbu_20_2` |
| `hacim` | `volume` |
| `bbm_20.5_2` | `bbm_20p5_2` |

CSV yazarken kanonik isimler tercih edilir; ham adlar da otomatik
normalizasyon ile çalışır.

## Hızlı Başlangıç
Aşağıdaki komutlar örnek verilerle çevrimdışı çalışır.

```bash
# filtre modülünü doğrula
python -m backtest.cli dry-run --filters-module io_filters --filters-include "*"

# Excel dosyalarını Parquet'e çevir
python -m backtest.cli convert-to-parquet --out data/parquet

# Tek gün tarama yap
python -m backtest.cli scan-day \
  --data data/BIST.xlsx --filters-module io_filters --filters-include "*" \
  --date 2024-01-02 --out raporlar/gunluk
```

```python
from backtest.filters_compile import compile_expression
import pandas as pd

df = pd.DataFrame({"a": [1, 2, 3], "b": [0, 1, 2]})
fn = compile_expression("cross_up(a,b)")
print(fn(df))
```

## Filtre Modülü

Filtre tanımları artık CSV dosyaları yerine Python modülleriyle
sağlanır. Varsayılan `io_filters` modülü `[{"FilterCode": "FI",
"PythonQuery": "True"}]` tanımlar ve tüm örneklerde kullanılır.

## Sorun Giderme & Detaylı Kullanım
Ek argümanlar, tüm alt komutlar ve ipuçları için
[`USAGE.md`](USAGE.md) dosyasına bakın.
