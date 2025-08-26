# CLI & Feature Flags (A7)

## Amaç
- Güvenli varsayılanlar, hataya dayanıklı argüman işleme, açık yardım metinleri.
- Feature flag'lerle davranışın kontrolü (ör. `dry_run`, `write_outputs`).

## Varsayılanlar
- `dry_run = true`
- `write_outputs = true` (yalnız `scan-*` komutlarında)
- `log_level = INFO`

## Bayraklar (genel)
- `--config path.yaml` (opsiyonel)
- `--log-level {DEBUG,INFO,WARNING,ERROR}`
- `--dry-run` → doğrulama modunu çalıştır (A4)

## Komutlar
- `scan-day --data <path> --date YYYY-MM-DD --filters-module io_filters --filters-include "*" --out dir [--alias alias.csv] [--no-write]`
- `scan-range --data <path> --start YYYY-MM-DD --end YYYY-MM-DD --filters-module io_filters --filters-include "*" --out dir [--alias alias.csv] [--no-write]`

Örnek:
`python -m backtest.cli scan-day --config config/scan.yml --filters-module io_filters --filters-include "*"`

## Filters configuration

```yaml
filters:
  module: "io_filters"
  include: ["*"]
```

Tam örnek için `examples/example_filters_module.yml` dosyasına bakın.

## Hata Kodları (CLI)
- CL001: Argüman eksik/uyumsuz
- CL002: Dosya yolu yok/erişilemedi
- CL003: `--no-write` ile çıktı yazımı devre dışı (bilgi notu)

## Kabul Kriterleri
- Yanlış argümanlarda anlamlı hata mesajı + çıkış kodu 2
- Varsayılanlar config dosyası ve env ile override edilebilir
- `--no-write` ile dosya yazımı yapılmadan sadece konsol özeti basılır
