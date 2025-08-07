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
- Zorunlu kolonlar:

| Kolon | Açıklama |
| ----- | ----- |
| FilterCode | Filtrenin raporda görünecek kısa adı |
| PythonQuery | `pandas` ifadesi, örn: `(rsi_14 > 65) and (relative_volume > 1)` |

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


## Sürüm Notları
- 1.1.0: Colab desteği ve yeni README.
- 1.0.0: İlk yayımlanan sürüm.

