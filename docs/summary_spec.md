# Tarama Ortalamaları & BİST’e Oranlı Özetler (A9)

## Amaç
Günlük sinyal dosyalarından (A6) hareketle, her gün için **eşit ağırlıklı** sinyal portföyünün H=1 (t+1) getirilerini hesaplamak; aynı günün **BİST (XU100) getirisi** ile karşılaştırıp **alpha** (portföy – BİST) üretmek. Ayrıca filtre bazında sinyal sayıları ve kapsam raporları çıkarılır.

## Girdi
- Günlük sinyaller: `raporlar/gunluk/YYYY-MM-DD.csv` (date,symbol,filter_code)
- Fiyat paneli: `data.parquet` **veya** `prices.csv` (index=Date; tek sembol için kolonlar kanonik; çoklu sembolde MultiIndex: (symbol, field))
- BİST verisi: `benchmark.csv|xlsx` (kolonlar: `date`, `close`) veya config ile belirtilen yerden.

## Varsayılanlar
- Ufuk (H): **1 iş günü** (Aşama-1 için sabit)
- Ağırlık: **eşit ağırlık** (aynı gün sinyalleri)
- NaN politikası: Gerekli günlerden biri eksikse o gözlem **hariç** (coverage sayılır)

## Çıktılar
- `raporlar/ozet/daily_summary.csv`: `date, signals, filters, coverage, ew_ret, bist_ret, alpha`
- `raporlar/ozet/filter_counts.csv`: `date, filter_code, count`
- (opsiyonel) `raporlar/ozet/summary.md`: kısa tablo ve metrikler

## Tanımlar
- **ew_ret**: Aynı gün sinyal veren sembollerin **t→t+H** getirilerinin eşit ağırlıklı ortalaması.
- **bist_ret**: Aynı gün BİST kapanışının **t→t+H** getirisi.
- **alpha**: `ew_ret - bist_ret`

## Hata Kodları
- SM001: Benchmark yüklenemedi veya kolonlar eksik
- SM002: Fiyat panelinde gerekli kolon(lar) yok (`close` en azından)
- SM003: Sinyal dosyası bulunamadı/boş

## Kabul Kriterleri
- En az 3 ardışık gün için `daily_summary.csv` yazılır.
- `alpha` doğru hesaplanır (sentetik testlerle doğrulanır).
- Çoklu sembolde MultiIndex kolon yapısı desteklenir.
