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

İsteğe bağlı olarak testleri çalıştırmak için:

```bash
pytest -q
```
