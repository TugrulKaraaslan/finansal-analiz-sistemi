# CLI & Feature Flags (A7)

## Amaç
- Güvenli varsayılanlar, hataya dayanıklı argüman işleme, açık yardım metinleri.
- Feature flag'lerle davranışın kontrolü (ör. `dry_run`, `filters_enabled`, `write_outputs`).

## Varsayılanlar
- `dry_run = true`
- `filters_enabled = true`
- `write_outputs = true` (yalnız `scan-*` komutlarında)
- `log_level = INFO`

## Bayraklar (genel)
- `--config path.yaml` (opsiyonel)
- `--log-level {DEBUG,INFO,WARNING,ERROR}`
- `--filters-off` → `filters_enabled = false`
- `--dry-run` → doğrulama modunu çalıştır (A4)

## Komutlar
- `dry-run --filters filters.csv [--alias alias.csv]`
- `scan-day --data <path> --date YYYY-MM-DD --filters filters.csv --out dir [--alias alias.csv] [--filters-off] [--no-write]`
- `scan-range --data <path> --start YYYY-MM-DD --end YYYY-MM-DD --filters filters.csv --out dir [--alias alias.csv] [--filters-off] [--no-write]`

## Hata Kodları (CLI)
- CL001: Argüman eksik/uyumsuz
- CL002: Dosya yolu yok/erişilemedi
- CL003: `--no-write` ile çıktı yazımı devre dışı (bilgi notu)

## Kabul Kriterleri
- Yanlış argümanlarda anlamlı hata mesajı + çıkış kodu 2
- Varsayılanlar config dosyası ve env ile override edilebilir
- `filters_off` iken filtreler uygulanmaz (sadece veri/indikatör hazırlığı)
- `--no-write` ile dosya yazımı yapılmadan sadece konsol özeti basılır
