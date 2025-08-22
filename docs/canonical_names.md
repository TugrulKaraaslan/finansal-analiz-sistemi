# Kanonik İsim Sözlüğü – Kural Seti (Aşama 1)

## Amaç
Filtre–veri eşleşmesini garanti etmek için **tek ve net** bir kanonik isim standardı tanımlar.

## Kural Özeti
- **Biçim**: küçük harf + `snake_case`
- **Fiyat Alanları**: `open, high, low, close, volume, vwap_d`
- **Tarih Dizini**: günlük kapanışa göre; NaN karşılaştırmaları **False** kabul edilir
- **Parametre Gösterimi**: indikatör adından sonra `_` ile eklenir: `rsi_14`, `ema_50`, `macd_12_26_9`, `bbh_20_2`
- **Bollinger**: `bbl_{n}_{k}`, `bbm_{n}_{k}`, `bbh_{n}_{k}`
- **MACD**: `macd_{fast}_{slow}_{signal}`, `macd_signal_{fast}_{slow}_{signal}`, `macd_hist_{fast}_{slow}_{signal}`
- **Directional**: `adx_{n}`, `dmp_{n}`, `dmn_{n}`
- **Aroon**: `aroon_up_{n}`, `aroon_down_{n}`
- **StochRSI**: `stochrsi_k_{rsi_len}_{stoch_len}_{smooth}`, `stochrsi_d_{rsi_len}_{stoch_len}_{smooth}`
- **Değişim**: `change_1d_percent`, `change_1w_percent` (1w = 5 iş günü)
- **Hacim**: `relative_volume` (son x güne göre; x ileride konfigüre edilir)

## Örnek Kanonikler
```
open, high, low, close, volume, vwap_d
sma_20, ema_50, wma_20, rsi_14
macd_12_26_9, macd_signal_12_26_9, macd_hist_12_26_9
bbl_20_2, bbm_20_2, bbh_20_2
adx_14, dmp_14, dmn_14
aroon_up_14, aroon_down_14
stochrsi_k_14_14_3, stochrsi_d_14_14_3
change_1d_percent, change_1w_percent, relative_volume
```

## Hata Kodları (ilgili)
- VF001: Bilinmeyen seri adı
- VC001: `FilterCode` tekrarı
- VC002: `PythonQuery` boş

> Not: Bu dosya Aşama-1 boyunca **tek gerçek** kanoniktir. Yeni isim eklemek → PR.
