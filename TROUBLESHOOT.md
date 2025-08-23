# Troubleshoot

## PermissionError: '/content'
Colab'a özgü `/content` yolu yerel veya CI ortamında yazılabilir değildir. `paths.py` içindeki mantık gereği `EXCEL_DIR`'i ayarla ya da `CI=true` ortam değişkeni ile depo kökündeki `veri_guncel_fix/` dizini kullan.

## ModuleNotFoundError: hypothesis
Testler sırasında `hypothesis` modülü bulunamazsa geliştirme bağımlılıklarını yükleyin:

```bash
pip install -r requirements-dev.txt
```

## filters.csv bulunamadı
Filtre dosyası yol çözümü şu önceliği izler: CLI argümanı > YAML config > depo kökündeki `filters.csv`.

```bash
python -m backtest.cli scan-range --filters-csv config/filters.csv
```

## Preflight Unknown tokens
Preflight raporu bilinmeyen token'lar gösteriyorsa filtre ifadelerindeki kolon veya gösterge isimlerini kontrol edin. Preflight, `ema_20`, `rsi_14`, `stochd_14_3_3`, `psar...` gibi kanonik isimleri regex whitelist'iyle tanır. Bunun dışındakiler varsayılan olarak hataya yol açar; uyarıya çevirmek için `PREFLIGHT_ALLOW_UNKNOWN=1` ortam değişkenini kullanabilirsiniz. Alias kullanımının nasıl kanonikleştirildiği için [docs/ALIAS_POLICY.md](docs/ALIAS_POLICY.md) dosyasına bakın.

## Preflight legacy alias hatası
`its_9`, `macd_12_26_9`, `bbm_20 2` gibi legacy alias'lar preflight aşamasında
varsayılan olarak hatadır. Lokal geliştiriciler `--allow-alias` bayrağı veya YAML
config içinde `allow_alias: true` ile bu kontrolü geçici olarak uyarıya
çevirebilir; CI'da bu seçenekler yok sayılır. Alias'ları düzeltmek için:

```bash
python tools/canonicalize_filters.py filters.csv filters_canonical.csv
```
