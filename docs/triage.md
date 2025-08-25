# Triage Rehberi

## TRIAGE CHECKLIST

### DATA
- `DATA` olayındaki `rows`, `symbols`, `date_min`, `date_max` alanlarını kontrol et.
- `DATA_EMPTY` olayları veri setinin neden boş olduğunu (`reason`) söyler.

### FILTERS
- `FILTERS` olayındaki `n_filters` toplamına bak.
- `invalid`, `missing` veya `unsafe` sayıları sıfır olmalı.

### SCREENER
- Her gün için `FILTER_RESULT` olaylarında `hits` değerlerini izle.

### BACKTEST
- `TRADE` olaylarında gün bazında işlemleri say.
- `NO_TRADES_DAY` olayları işlem olmayan günleri listeler.

### REPORT
- `WRITE_DAY` ve `WRITE_RANGE` olayları yazılan satır sayılarını bildirir.

### ZERO_RESULT_RANGE
- Hiç sonuç çıkmadığında `ZERO_RESULT_RANGE` olayındaki `first_zero_day` alanı "ilk nerede sıfırlandı?" sorusuna yanıt verir.

## events.jsonl nasıl okunur?
`events.jsonl` dosyası satır başına JSON içerir; sorgulamak için `jq` veya Python kullanılabilir.

### jq
```bash
# DATA özetini getir
jq 'select(.event == "DATA") | {rows, symbols, date_min, date_max}' loglar/run_*/events.jsonl

# İlk sinyal gelen günü bul
jq 'select(.event == "FILTER_RESULT" and .hits > 0) | .date' loglar/run_*/events.jsonl | head -n 1
```

### Python
```python
import json
from pathlib import Path

run = next(Path('loglar').glob('run_*/events.jsonl'))
with run.open() as f:
    events = (json.loads(line) for line in f)
    for ev in events:
        if ev['event'] == 'ZERO_RESULT_RANGE':
            print('first zero day:', ev['first_zero_day'])
            break
```
