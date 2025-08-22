# PythonQuery DSL – Aşama 1 (Güvenli AST & Kesişim Semantiği)

## Amaç
`filters.csv` içindeki `PythonQuery` ifadelerini **güvenli**, **deterministik** ve **okunur** şekilde değerlendirmek.

## Temel Kurallar
- **Güvenlik:** Python `eval` YOK. Sadece `ast.parse(..., mode="eval")` + **whitelist** node yürütme.
- **İzinli Node'lar:** `Expression, BoolOp, UnaryOp, BinOp(+,-,*,/,%), Compare, Name, Constant(Num), Call, Load, And/Or/Not`.
- **İzinli Operatörler:** `+ - * / %`, karşılaştırmalar `> < >= <= == !=`, mantık `and or not`.
- **İsimler:** Yalnız **kanonik** seri/fonksiyon isimleri. (Bkz. `docs/canonical_names.md`).
- **NaN Politikası:** Karşılaştırmalarda NaN → **False**. Mantık operatörleri numpy/pandas kuralları ile vektörel.
- **Zaman Penceresi:** `cross_*` için `t-1` ve `t` zorunlu; veri eksikse **False**.

## Fonksiyonlar (Aşama-1)
- `cross_up(a, b)`  ⇢  `(a[t-1] ≤ b[t-1]) and (a[t] > b[t])`
- `cross_down(a, b)` ⇢  `(a[t-1] ≥ b[t-1]) and (a[t] < b[t])`
- İleride (Aşama-1 boyunca) eşik/fonksiyonlar genişletilebilir (PR ile).

## Örnek İfadeler
- `rsi_14 > 55 and close > ema_50`
- `cross_up(macd_12_26_9, macd_signal_12_26_9)`
- `close > bbh_20_2 and volume > 2 * relative_volume`

## Hata Kodları
- **DF001**: DSL parse hatası (syntaks)
- **DF002**: Yasak AST düğümü/operatör
- **DF003**: Tanımsız isim (seri/fonksiyon)
- **DF004**: Fonksiyon bağımsız değişken hatası

## Kabul Kriterleri
- 10+ örnek ifade **parse** edilir ve **vektörel** doğru sonuç üretir.
- `cross_*` semantiği altın testlerde **bire bir** doğrulanır.
- Hiçbir yerde Python `eval` YOK; whitelist geçişi zorunlu.
