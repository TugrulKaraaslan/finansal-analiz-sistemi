## Stage1 İlerleme – A1 Tamam
- Kanonik isimler ve alias tablo eklendi.
- Kod katmanı: `backtest/naming/*` (normalize & alias)
- Bu katman A4 Dry-Run doğrulamada ve A5 ön-hesaplayıcıda yeniden kullanılacak.

## Stage1 İlerleme – A2 Tam
- PythonQuery DSL eklendi: Güvenli AST whitelist, `cross_up/down` semantiği.
- Modüller: `backtest/dsl/*`
- Test: `tests/test_dsl_basic.py`

## Stage1 İlerleme – A3 Tam
- In‑memory normalize katmanı eklendi: alias→kanonik, snake_case, .1 kopya tespiti.
- Politikalar: strict (hata), prefer_first (drop), suffix (rename _dupN).
- Modüller: `backtest/normalize/*`
- Test: `tests/test_normalize_df.py`
