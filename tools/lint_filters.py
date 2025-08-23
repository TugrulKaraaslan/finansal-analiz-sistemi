import sys
import re
import csv
from pathlib import Path

import pandas as pd
import yaml

CFG = Path('config/colab_config.yaml')
FILT = Path('filters.csv') if Path('filters.csv').exists() else Path('config/filters.csv')

assert CFG.exists(), 'missing config/colab_config.yaml'
assert FILT.exists(), 'missing filters.csv'

cfg = yaml.safe_load(open(CFG))
excel = Path(cfg['data']['excel_dir'])
if not excel.exists():
    excel = (Path.cwd() / excel.name).resolve()
assert excel.exists(), f'excel_dir yok: {excel}'

from glob import glob
xls = sorted(glob(str(excel) + '/*.xlsx'))
assert xls, f'Excel bulunamadı: {excel}'
cols = set(pd.ExcelFile(xls[0]).parse(0, nrows=0).columns)

ident = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")
legacy = {'its_9','iks_26','macd_12_26_9','macds_12_26_9','bbm_20 2','bbu_20 2','bbl_20 2'}
allow_funcs = {'cross_up','cross_down'}

bad = {}
with open(FILT, encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        expr = (row.get('PythonQuery') or '').strip()
        for t in ident.findall(expr):
            if t in allow_funcs or t in legacy:
                continue
            if t not in cols and t.lower() not in {c.lower() for c in cols}:
                bad.setdefault(row.get('FilterCode'), set()).add(t)

if bad:
    for k, v in bad.items():
        print(f"BAD TOKENS in {k}: {sorted(v)}")
    sys.exit(2)
print('lint passed')
