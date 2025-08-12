# Google Colab Hızlı Başlangıç

Aşağıdaki tek hücre Colab ortamında projeyi kurar, pandas_ta için NumPy 2 yamasını uygular ve kısa bir backtest çalıştırır. Hücreyi olduğu gibi kopyalayıp çalıştırabilirsiniz.

```python
%pip install -U pip
%pip install -r requirements_colab.txt

import os
os.system(r"grep -rl 'from numpy import NaN' /usr/local/lib/python*/dist-packages/pandas_ta | xargs -r sed -i 's/from numpy import NaN/from numpy import nan/g'")
os.system(r"grep -rl 'np\\.NaN'              /usr/local/lib/python*/dist-packages/pandas_ta | xargs -r sed -i 's/np\\.NaN/np.nan/g'")

%cd /content/finansal-analiz-sistemi
%env PYTHONPATH=/content/finansal-analiz-sistemi
!mkdir -p raporlar

import numpy as np, pandas as pd, pandas_ta as ta
print("NumPy:", np.__version__, "| Pandas:", pd.__version__)
print("pandas-ta import OK")

!python -m backtest.cli scan-range --config config_scan.yml \
  --start 2025-03-07 --end 2025-03-11 \
  --holding-period 1 --transaction-cost 0.0005

!ls -la raporlar | head
```

## İsim normalizasyonu

Veri dosyalarındaki ve filtre ifadelerindeki tüm sütun isimleri otomatik olarak
`lower_snake_case` biçimine dönüştürülür. Örneğin kullanıcı `EMA20` ya da
`ema-20` yazsa bile sistem bunu `ema_20` olarak yorumlar. Bu sayede veri
kaynakları ve filtreler arasında tutarlılık sağlanır.

Desteklenen varyantların kanonik karşılıklarını görmek veya `filters.csv`
dosyasındaki sorguları düzeltmek için:

```bash
python tools/audit_names.py --write-fixes
```

Bu komut örnek veri dosyasındaki ham → kanonik sütun adlarını ve filtrelerdeki
isim dönüşümlerini raporlar; `filters_fixed.csv` dosyasını üretir.

İsteğe bağlı olarak testleri çalıştırmak için:

```bash
pytest -q
```
