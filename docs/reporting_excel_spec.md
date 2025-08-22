# Excel Raporları (A10)

## Amaç
A9 çıktılarından tek bir Excel dosyası üretmek: trend izleme, paylaşım, arşiv kolaylığı.

## Girdi
- `raporlar/ozet/daily_summary.csv`
- `raporlar/ozet/filter_counts.csv`
- (opsiyonel) `raporlar/gunluk/*.csv` 

## Çıktı
`raporlar/ozet/summary.xlsx` (sayfalar):
1. `DAILY_SUMMARY` → `date,signals,filters,coverage,ew_ret,bist_ret,alpha`
2. `FILTER_COUNTS` → `date,filter_code,count`
3. `KPI` → toplam gün, ort. alpha, pozitif alpha gün yüzdesi, ort. sinyal/adet
4. `PIVOT_FILTER_BY_DAY` → satır=day, sütun=filter_code, değer=count
5. `README` → üretim tarihi, versiyon, run_id (A8 entegrasyonu varsa)

## Biçimlendirme Kuralları
- Tarihler ISO-8601; sayı biçimleri: `ew_ret,bist_ret,alpha` → yüzde (2 hane)
- Başlık satırı kalın; tablo kenarlıkları ince gri
- Otomatik sütun genişliği
- `alpha` için koşullu biçim: negatif kırmızı, pozitif yeşil

## Hata Kodları
- XR001: Girdi dosyası(ları) bulunamadı
- XR002: Excel yazımı başarısız (izin/kilit)

## Kabul Kriterleri
- Excel dosyası oluşur ve en az 4 sayfa içerir
- KPI sayfası doğru metrikleri hesaplar
- Örnek veriyle birim testler geçer
