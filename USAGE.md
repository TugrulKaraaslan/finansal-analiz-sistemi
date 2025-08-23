# Usage

## 1. Kurulum

```bash
python -m venv .venv && source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

## 2. Fixture üretimi

```bash
make fixtures
```

Bu komut `veri_guncel_fix/` altındaki Excel dosyalarından test için küçük örnekler oluşturur.

## 3. Preflight

```bash
make preflight
```

Preflight, `filters.csv` içindeki token'ların Excel kolonlarıyla uyuştuğunu doğrular. Gerekirse CLI'da `--no-preflight` bayrağı veya YAML'da `preflight: false` ile atlanabilir.

## 4. Taramayı çalıştır

```bash
python -m backtest.cli scan-range --config config_scan.yml --start 2025-03-07 --end 2025-03-11
```

### Filtre dosyası yol çözümü

Yol önceliği: CLI argümanı > YAML config > proje varsayılanı (`filters.csv`).

```bash
python -m backtest.cli scan-range --filters-csv config/filters.csv --start 2025-03-07 --end 2025-03-11
```

`--filters-csv my/filters.csv` kullanıldığında YAML içeriği yok sayılır ve belirtilen dosya kullanılır.

## 5. Sonuçlar

Çalışma tamamlandığında raporlar `raporlar/` dizinine, loglar `loglar/` dizinine yazılır.

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
