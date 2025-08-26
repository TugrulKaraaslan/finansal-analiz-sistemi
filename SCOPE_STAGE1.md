# AŞAMA 1 – BACKTEST: KAPSAM TANIMI (SCOPE_STAGE1.md)

## 0. Amaç (kısa)
03.01.2022 – 18.04.2025 aralığında **gün-gün tarama** çalıştırıp:
- Günlük sinyal dosyaları üretmek,
- **Tarama Ortalamaları** tablosu ve **BİST’e Oranlı** özet tabloyu çıkarmak.
Hedef: Basit ama hatasız, tekrarlanabilir ve denetlenebilir çıktı.

## 1. Kapsam (yapılacaklar)
- **Veri**: Günlük OHLCV, evren: **BIST100 hisseleri** + **BIST100 endeksi (XU100)**.
- **İsim standardı**: Küçük harf + snake_case, referans pandas-ta.
- **Filtre dili (PythonQuery)**: AST whitelist ile güvenli; `cross_up/cross_down` dahil.
- **Dry-run**: Fail-fast doğrulama (şema, isim, ifade).
- **Batch**: İşlem günlerine göre günlük tarama döngüsü.
- **Özetler**: Tarama Ortalamaları & BIST’e Oranlı tablolar.
- **Log & İzlenebilirlik**: run_id, parametre snapshot, süreler, hata kodları.

## 2. Kapsam dışı
MACD histogram rengi, "en iyi hisse seçimi", canlı tarama, portföy kuralları, optimizasyon, dashboard.

## 3. Girdiler
- Fiyat verisi, filtre modülü, alias_mapping.csv, config.

## 4. Çıktılar
- Günlük sinyaller: `raporlar/gunluk/YYYY-MM-DD.csv`
- Özetler: `Tarama_Ortalamalari.csv`, `BISTe_Oranla_Tarama_Ort.csv`
- Log ve artefaktlar.

## 5. Tanımlar
- Tarama Ortalaması (T+1)
- BİST’e Oranlı (Alpha)

## 6. Emniyet Rayları
Eval yok, deterministik çalışma, NaN→False, isim standardı zorunlu, dry-run varsayılan.

## 7. Kabul Kriterleri
1) filtre modülü hatasız
2) Örnek 3 gün sinyalleri tutar
3) Özet tablolar ±0.0001 sapma
4) Log/artefakt tam

## 8. Hata Kodları
VC001, VC002, VF001, VF002, VF003, VD001, VR001

## 9. Bağımlılıklar
pandas, numpy, pandas-ta, openpyxl, pyarrow. TA-Lib yok.

## 10. Değişiklik Yönetimi
Sadece `CHANGE_POLICY.md` süreciyle.
