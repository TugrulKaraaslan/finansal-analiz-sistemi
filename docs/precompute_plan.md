# Ön Hesaplayıcı Katmanı (A5)

## Amaç
Filtrelerde kullanılan göstergeleri (örn. `rsi_14`, `ema_50`, `macd_12_26_9`) **önceden** hesaplayıp DataFrame’e eklemek.

## Kurallar
- **Tek Kaynak**: `canonical_names.md` → yalnız tanımlı göstergeler hesaplanır.
- **Yeniden Hesaplama Yok**: Aynı gösterge yalnızca 1 kez hesaplanır.
- **Bağımlılıklar**: `pandas`, `pandas_ta`.
- **NaN Politikası**: Göstergenin lookback süresinden önceki değerler NaN → doldurulmaz.
- **Performans**: Göstergeler topluca hesaplanır, for‑loop yok.

## Hata Kodları
- PC001: Desteklenmeyen gösterge ismi
- PC002: Parametre parse hatası

## Kabul Kriterleri
- `rsi_14`, `ema_50`, `sma_20`, `macd_12_26_9`, `bbh_20_2` gibi göstergeler başarıyla hesaplanır.
- Aynı gösterge birden fazla filtrede kullanılsa bile yalnız 1 kez hesaplanır.
- Çıktılar DataFrame’e yeni kolon olarak eklenir.
