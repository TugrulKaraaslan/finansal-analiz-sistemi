# Normalize Katmanı (A3) — In‑Memory

## Amaç
Veri kaynaklarından (CSV/Excel/Parquet) gelen kolon adlarını **in‑memory** olarak tek tip hale getirmek:
- **Alias→Kanonik** (A1 `data/alias_mapping.csv` referansı)
- **snake_case** (küçük harf + alt çizgi)
- **.1, .2 vb. kopyaların** tespiti
- **Çakışma/Belirsizlik raporu** (yazma yok; yalnız rapor)

## Kurallar
- **Yalnız bellek içinde** çalışır; disk/depo üzerinde **değişiklik YOK**.
- Alias çözümü **önce**, snake_case **sonra**.
- Aynı kanonik isme düşen birden fazla kolon → **çakışma** (VN001) olarak raporlanır.
- Alias CSV başlıkları **`alias,canonical_name`** olmalıdır.
- Türkçe karakterler normalize edilir (örn. `ı→i`, boşluk→`_`).

## Politikalar
- `policy="strict"` (varsayılan): Çakışma varsa **hata** yükselt ve mapping uygulama.
- `policy="prefer_first"`: İlk görüleni tut, diğerlerini **drop list**’e ekle.
- `policy="suffix"`: Çakışanlara `_dupN` son eki ver (`close, close_dup1, ...`).

## Hata Kodları
- **VN001**: Kanonik isim çakışması (ör. `Adj Close`, `Close`, `Close.1` hepsi `close`).
- **VN002**: Alias çakışması (aynı alias iki farklı kanonik ile eşleşmek istiyor).
- **VN003**: Alias CSV başlığı hatalı.

## Çıktı Raporu Şeması
```json
{
  "mapping": {"orijinal": "kanonik"},
  "collisions": [
    {"canonical": "close", "originals": ["Close", "Adj Close", "Close.1"]}
  ],
  "dropped": ["Close.1"],
  "renamed": ["Open->open", "VOL->volume", ...]
}
```

## Kabul Kriterleri
- A1 kanonik set ve alias CSV ile **uyumlu**.
- `strict` modda çakışmalar **hata** verir; diğer modlarda rapor döner.
- NaN davranışına dokunulmaz; yalnız kolon adları normalize edilir.
