# A12 — 2025-08-23

## Highlights
- A12 Test Paketi: Unit + Integration + Property + Golden (deterministik golden akışı)
- Filters path hardening ve güvenli eval; kontrollü legacy alias haritası
- CI sertleşmesi: `/content` bağımlılığı kaldırıldı; workspace-temelli `artifacts/`
- Excel fixtures: binary xlsx'ler repodan çıkarıldı; CI'da runtime oluşturma
- Preflight doğrulayıcı: kolon/token kontrolü, indicator whitelist kalıpları
- Alias politikası: CI'da canonical-only enforcement (araştırma politikası ile hizalı)
- CI tetikleyici düzeltmesi: her PR'da testler koşuyor; branch protection önerisi
- Golden otomasyonu: `make golden[-verify]` + pre-commit ile otomatik güncelleme
- Docs & DX: README/USAGE/FAQ/TROUBLESHOOT, `make check` toplu hedefi

## Upgrade Guide
- `pip install -r requirements-dev.txt`
- `make check`

## Checks
- [ ] CI green
- [ ] Golden up-to-date
- [ ] Preflight (alias forbid) temiz
