# Loglama & İzlenebilirlik (A8)

## Amaç
- Her koşuya benzersiz **run_id** atamak.
- Girdi parametreleri ve ortamı **artefakt** olarak saklamak.
- Çıktılar için **checksum** üretip deterministik tekrarları doğrulamak.

## run_id Biçimi
`YYYYMMDD_HHMMSS_<8-char>` (örn. `20250107_213045_a1b2c3d4`).

## Artefaktlar
- `artifacts/<run_id>/config.json` → CLI bayrakları + config birleşimi
- `artifacts/<run_id>/env.json` → Python sürümü, paket sürümleri (pandas/numpy), git kısa hash (varsa)
- `artifacts/<run_id>/inputs.json` → data path, filtre path, tarih aralığı, evren bilgisi
- `artifacts/<run_id>/checksums.json` → üretilen dosyaların SHA256 değerleri

## Loglama
- Format: `timestamp | LEVEL | logger | message`
- Yol: `logs/<run_id>.log`
- Varsayılan seviye: `INFO` (A7 config ile uyumlu)

## Determinizm
- Aynı data + aynı filtre + aynı tarih aralığı + aynı kod sürümü → **aynı checksum**.
- Farklı koşullarda değişiklik olduğunda değişen artefaktlarda iz bırakılır.

## Hata Kodları
- LG001: Artefakt dizini oluşturulamadı
- LG002: Config/env snapshot yazılamadı
- LG003: Checksum üretim hatası

## Kabul Kriterleri
- Koşu sonunda `logs/<run_id>.log` ve `artifacts/<run_id>/*` dosyaları oluşur.
- Üretilen her `raporlar/gunluk/*.csv` için checksums.json’da kayıt vardır.
- Tekrar koşuda, aynı girdilerle checksum’lar eşleşir.
