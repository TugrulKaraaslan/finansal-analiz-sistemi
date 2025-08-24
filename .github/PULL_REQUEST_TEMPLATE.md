## Summary

<!-- Kısa, öz değişiklik açıklaması -->

## Checklist
- [ ] Offline varsayılan korunuyor (indirme default off)
- [ ] Tek veri kaynağı `data/` (legacy path yok)
- [ ] `backtest/paths.py` merkezli path kullanımı
- [ ] CLI yardım çıktısı çalışıyor
- [ ] Testler yeşil (CI & lokal)
- [ ] Docs güncel (README_STAGE1/USAGE/TROUBLESHOOT/FAQ)

## Risk/rollback
<!-- Riskler ve geri alma planı -->

## Doğrulama
```bash
python -m backtest.cli --help
pytest -q
grep -RIn "veri_guncel_fix" backtest utils tools tests
```
