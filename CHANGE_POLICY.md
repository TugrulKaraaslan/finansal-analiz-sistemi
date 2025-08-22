# DEĞİŞİKLİK POLİTİKASI (CHANGE_POLICY.md)

## İlke
- Küçük PR, test zorunlu, ana dal korumalı.

## PR Süreci
- Branch: stage1/<kısa-konu>
- Commit: Conventional style
- PR şablonu: Amaç, çıktı, test, risk, kabul kriterleri
- Onay + tüm testler yeşil → merge

## Test Kapısı
Unit, integration, golden, property.

## Feature Flag
- filters_enabled = true
- dry_run = true (varsayılan)

## Geri Alma
Her PR öncesi etiket, revert ile geri dönüş.

## Güvenlik
Eval yok, AST whitelist, yeni bağımlılık lisans kontrolü.

## Performans
İndikatör ön-hesap, Parquet, chunking.

## Sonrası
Merge → README_STAGE1.md güncelle, sürüm etiketi.
