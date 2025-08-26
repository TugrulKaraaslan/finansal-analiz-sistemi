# Dry‑Run Doğrulama (A4) – Plan

## Amaç
`filters.csv` içindeki filtrelerin ve veri kolonlarının geçerliliğini **çalıştırmadan önce** kontrol etmek.

## Doğrulanan Alanlar
1. **CSV Şeması**
   - `FilterCode` boş değil, tekil olmalı
   - `PythonQuery` boş olmamalı
2. **DSL İfadeleri**
   - AST parse hatası yok
   - Yalnız izinli node/operatör
3. **Kanonik İsimler**
   - Tüm seri adları `canonical_names.md` içinde bulunmalı
   - Alias kullanımı varsa `alias_mapping.csv` ile çözümlenmeli
4. **Fonksiyonlar**
   - Yalnız izinli DSL fonksiyonları (`cross_up, cross_down`)
5. **Lookback**
   - İfade kullanılan indikatör için yeterli geçmiş gün veri olmalı (örn. `rsi_14` için ≥14 gün). Bu aşamada yalnız uyarı/rapor (yetersizse VD001).

## CLI Kullanımı
```bash
python -m backtest.cli \-\-filters filters.csv --dry-run
```

Çıktı: Hata/uyarı raporu. Başarılı ise: `✅ Uyum Tam`

## Hata Kodları
- VC001: FilterCode tekrarı
- VC002: PythonQuery boş
- VF001: Bilinmeyen seri adı
- VF002: Bilinmeyen fonksiyon
- VF003: Yasak AST düğümü
- VD001: Yetersiz lookback

## Kabul Kriterleri
- Hatalı filtreler **satır bazında** raporlanır
- Temizse CLI çıktısı `✅ Uyum Tam`
- Golden test ile doğrulama yapılır
