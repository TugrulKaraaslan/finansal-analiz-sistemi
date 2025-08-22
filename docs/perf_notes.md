# Performans Notları (A11)

## Amaç
400+ hisse × 3+ yıl × 300+ filtreyi makul sürede çalıştırmak. Önce demo evren: BIST30.

## Ölçümler
Tablo biçimi:
| symbols | days | filters | total_time | io_time | compute_time | peak_mem | workers | chunk_size | cache_hit% |
|---------|------|---------|------------|---------|--------------|----------|---------|------------|------------|

## Kabul Kriterleri
- BIST30 demo 3 yıl × 300 filtre ≤ hedef süre (örn. 20 dk).
- İyileştirme sonrası ≤10 dk.
- Determinism korunur (aynı input → aynı output checksum).
