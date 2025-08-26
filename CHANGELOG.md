# Changelog

## Unreleased

- filters.csv ve türevleri kaldırıldı; filtre tanımları modül tabanlı hale geldi

## A12 — 2025-08-23

**Öne çıkanlar**
- A12 Test Paketi: Unit + Integration + Property + Golden (deterministik golden akışı)
- Filters path hardening ve güvenli eval; kontrollü legacy alias haritası
- CI sertleşmesi: `/content` bağımlılığı kaldırıldı; workspace-temelli `artifacts/`
- Excel fixtures: binary xlsx'ler repodan çıkarıldı; CI'da runtime oluşturma
- Preflight doğrulayıcı: kolon/token kontrolü, indicator whitelist kalıpları
- Alias politikası: CI'da canonical-only enforcement (araştırma politikası ile hizalı)
- CI tetikleyici düzeltmesi: her PR'da testler koşuyor; branch protection önerisi
- Golden otomasyonu: `make golden[-verify]` + pre-commit ile otomatik güncelleme
- Docs & DX: README/USAGE/FAQ/TROUBLESHOOT, `make check` toplu hedefi

**İyileştirmeler**
- Hata iletileri: runner/evaluate ifadeyi kök nedenle birlikte raporluyor
- Make hedefleri: fixtures → preflight → lint → tests

**Kırıcı değişiklik yok** (kamu API'si değişmedi)
