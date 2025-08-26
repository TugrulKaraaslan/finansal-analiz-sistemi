# Günlük Batch Döngüsü (A6)

## Amaç
03.01.2022 – 18.04.2025 aralığındaki **her işlem gününde** filtreleri çalıştırıp, günlük sinyal dosyaları üretmek.

## Akış
1) **Girdi**: fiyat DataFrame'i (index=Date, kolonlar=kanonik), filtre modülü (ör. `io_filters`), `alias_mapping.csv` (opsiyonel)
2) **Normalize**: A3 katmanı ile kolonlar alias→kanonik + snake_case (in-memory)
3) **Dry-Run**: A4 katmanı ile filtre tanımlarının fail-fast kontrolü (hata varsa dur)
4) **Ön Hesap**: A5 katmanı ile gerekli göstergeleri tek seferde hesapla
5) **Günlük Döngü**: Her işlem günü için DSL (A2) ile bool mask üret; sinyalleri listele
6) **Yazım**: `raporlar/gunluk/YYYY-MM-DD.csv`
7) **Log/Artefakt**: `logs/YYYYMMDD_runid.log`, `artifacts/run_id_config.json`

## Girdi/Çıktı Yolları (varsayılan)
- Çıktı klasörü: `raporlar/gunluk/`
- Log klasörü: `logs/`
- Artefakt klasörü: `artifacts/`

## Hata Kodları (ilave)
- BR001: Çıktı dizini oluşturulamadı / yazma hatası
- BR002: Boş evren / tarih kesişimi yok
- BR003: Gün veri yok (o gün için DataFrame boş)

## Kabul Kriterleri
- En az 3 gün için sinyal dosyaları üretilir.
- Dosya adları `YYYY-MM-DD.csv` biçiminde.
- Sinyal satır şeması sabit: `date,symbol,filter_code`.
- Aynı gün/symbol/filter_code için **tekrar** yazım yok.
