## Stage1 İlerleme – A1 Tamam
- Kanonik isimler ve alias tablo eklendi.
- Kod katmanı: `backtest/naming/*` (normalize & alias)
- Bu katman A4 Dry-Run doğrulamada ve A5 ön-hesaplayıcıda yeniden kullanılacak.

## Stage1 İlerleme – A2 Tam
- PythonQuery DSL eklendi: Güvenli AST whitelist, `cross_up/down` semantiği.
- Modüller: `backtest/dsl/*`
- Test: `tests/test_dsl_basic.py`

## Stage1 İlerleme – A3 Tam
- In‑memory normalize katmanı eklendi: alias→kanonik, snake_case, .1 kopya tespiti.
- Politikalar: strict (hata), prefer_first (drop), suffix (rename _dupN).
- Modüller: `backtest/normalize/*`
- Test: `tests/test_normalize_df.py`

## Stage1 İlerleme – A4 Tam
- Dry‑Run doğrulama eklendi.
- CLI: `--dry-run` seçeneği filters.csv için fail-fast kontrol yapar.
- Rapor: satır, hata kodu, mesaj.

## Stage1 İlerleme – A5 Tam
- Ön hesaplayıcı eklendi.
- Gösterge hesaplamaları DataFrame’e önceden ekleniyor.
- Aynı gösterge bir kez hesaplanıyor (cache).
- Modüller: `backtest/precompute/*`
- Test: `tests/test_precompute.py`

## Stage1 İlerleme – A6 Tam
- Günlük batch döngüsü eklendi.
- CLI alt komutları: `scan-day`, `scan-range`.
- Çıktılar: `raporlar/gunluk/YYYY-MM-DD.csv` (date,symbol,filter_code).
- Modüller: `backtest/batch/*`
- Test: `tests/test_batch_runner.py`

## Stage1 İlerleme – A7 Tam
- CLI sertleştirildi: güvenli varsayılanlar, anlamlı hata kodları.
- Feature flags: `dry_run`, `filters_enabled`, `write_outputs`.
- Config dosyası ve log seviyesi desteği eklendi.

### A7 Hotfix (Compatibility)
- Eski testlere uyum için `scan_range/scan_day` click komutları ve `_run_scan`, `preflight`, `read_excels_long`, `compile_filters` sembolleri eklendi.
- `--report-alias` ve `--no-preflight` bayrakları yardım çıktısına taşındı.
- `load_config` artık attribute‑style nesne döndürüyor; legacy anahtarlar (`xu100_*`) destekleniyor.

## Stage1 İlerleme – A8 Tam
- run_id tabanlı log ve artefakt altyapısı eklendi.
- Artefaktlar: config/env/inputs snapshot ve günlük dosyaları için checksum.
- Aynı girdilerle tekrar koşuda checksum sabit → deterministik doğrulama.

## Stage1 İlerleme – A9 Tam
- Tarama ortalamaları ve BİST oranlı özetler eklendi (H=1, eşit ağırlık).
- Çıktılar: `raporlar/ozet/daily_summary.csv`, `filter_counts.csv`, `summary.md`.
- CLI: `summarize --data panel.parquet --signals raporlar/gunluk --benchmark bist.csv --out raporlar/ozet`.

## Stage1 İlerleme – A10 Tam
- Excel çıktı katmanı eklendi: `summary.xlsx` (DAILY_SUMMARY, FILTER_COUNTS, KPI, PIVOT_FILTER_BY_DAY, README).
- CLI: `report-excel --daily raporlar/ozet/daily_summary.csv --filter-counts raporlar/ozet/filter_counts.csv --out raporlar/ozet/summary.xlsx`.

## Stage1 İlerleme – A11 Tam
- Parquet panel ve sembol-chunk okuma eklendi.
- Tek hesap prensibi: indikatörler chunk bazında bir defa hesaplanıyor.
- Opsiyonel paralellik: `--workers` ile hisse bazlı fan-out.
- CLI örnek:
  ```bash
  python -m backtest.cli scan-range --config config.yaml --parquet-cache cache/panel.parquet --chunk-size 20 --workers 4
  ```
