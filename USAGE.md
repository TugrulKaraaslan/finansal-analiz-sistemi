# Usage

> A12 sürümü (2025-08-23) yayınlandı. Ayrıntılar için [CHANGELOG](CHANGELOG.md).

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

## Veri Kalitesi Sözleşmeleri

```bash
# Sözleşme kontrolü (lokalde)
make quality
# Rapor → artifacts/quality/report.json
```

Kuralları ve toleransları değiştirmek için `contracts/data_quality.yaml`
dosyasını düzenleyin. Şema ve mantık ihlalleri aracı başarısız kılar; tolerans
aşımları yalnızca uyarı üretir.

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

## Portfolio Motoru

Portföy motoru, sinyallerden pozisyon boyutları ve maliyetleri hesaplamak için kullanılır.

### Boyutlama Modları

- **risk_per_trade**: ATR tabanlı stop mesafesiyle her işlemde özsermayenin belirli bir bps'i riske edilir.
- **fixed_fraction**: Özsermayenin sabit bir yüzdesi pozisyona ayrılır.
- **target_weight**: Sinyal hedef ağırlık verirse doğrudan notional hesaplanır.

### Limitler

`config/portfolio.yaml` dosyasında max_positions, max_position_pct, max_gross_exposure, lot_size, min_qty gibi kısıtlar tanımlanır.

### Maliyet Entegrasyonu

`config/costs.yaml` mevcutsa `apply_costs` aracılığıyla komisyon, spread ve slippage maliyetleri uygulanır; yoksa maliyetler 0 kabul edilir.

### CLI Örneği

```bash
python -m backtest.cli portfolio-sim --config config/colab_config.yaml --portfolio config/portfolio.yaml --start 2025-03-07 --end 2025-03-09
```

Çıktılar `artifacts/portfolio/` klasörüne `trades.csv` ve `daily_equity.csv` olarak yazılır.

