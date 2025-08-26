# Google Colab Akışı

### Hücre 1 — Kurulum

```python
%pip install -U "pip>=23"
%pip install "pandas==2.1.4" "numpy==1.26.4" \
             "pyarrow>=14" "openpyxl>=3.1" "xlsxwriter>=3.2" \
             "tqdm>=4.66" "python-dateutil>=2.8" \
             "pandera>=0.18,<0.20" pandas-ta loguru PyYAML click
print("OK: Kurulum bitti. Eğer NumPy/Pandas yükseldiyse Runtime → Restart runtime, sonra Hücre 2.")
```

### Hücre 2 — Repo ve klasörler

```python
%cd /content
!git clone https://github.com/TugrulKaraaslan/finansal-analiz-sistemi.git || echo "Repo zaten var"
%cd /content/finansal-analiz-sistemi
!mkdir -p raporlar loglar config data cache
```

### Hücre 3 — Config yaz (mutlak yollar)

```python
%%writefile config/colab_config.yaml
project:
  out_dir: "raporlar"
  logs_dir: "loglar"
  run_mode: "range"
  holding_period: 1
  transaction_cost: 0.0
  stop_on_filter_error: false

data:
  excel_dir: "/content/finansal-analiz-sistemi/data"
  enable_cache: false
  cache_parquet_path: "cache"

  calendar:
    tplus1_mode: "calendar"
    holiday_csv: ""

  benchmark:
    source: "excel"
    excel_path: "/content/finansal-analiz-sistemi/data/BIST.xlsx"
    excel_sheet: "BIST"
    csv_path: ""
    column_date: "date"
    column_close: "close"

filters:
  module: "io_filters"
  include: ["*"]

report:
  with_bist_ratio_summary: true
  include_hit_ratio: true
  excel_engine: "xlsxwriter"

  range:
    start_date: "2022-01-03"
    end_date:   "2025-04-18"

  single:
    date: "2025-03-07"
  ```

  > `benchmark.source` "excel" ise `excel_path`'i mutlak yazmayı ve dosyanın ilk sheet adının **BIST** olduğundan emin olmayı unutma.

### Hücre 4 — Tarihi kolay değiştirme (opsiyonel)

```python
import yaml
p = yaml.safe_load(open("config/colab_config.yaml"))
# Örnek düzenleme:
# p["project"]["run_mode"] = "single"
# p["single"]["date"] = "2025-03-07"
yaml.safe_dump(p, open("config/colab_config.yaml","w"))
print("OK → run_mode:", p["project"]["run_mode"], "| single:", p["single"]["date"], "| range:", p["range"]["start_date"], p["range"]["end_date"])
```

### Hücre 5 — Tek gün çalıştır (scan-day)

```python
%cd /content/finansal-analiz-sistemi
!python -m backtest.cli scan-day --config config/colab_config.yaml --date 2025-03-07 | tee loglar/colab_run_$(date +%Y%m%d_%H%M%S).log
```

### Hücre 6 — Aralık çalıştır (scan-range)

```python
%cd /content/finansal-analiz-sistemi
!python -m backtest.cli scan-range --config config/colab_config.yaml --start 2022-01-03 --end 2025-04-18 | tee -a loglar/colab_run_$(date +%Y%m%d_%H%M%S).log
print("✅ Tamam. Raporlar: /content/finansal-analiz-sistemi/raporlar | Loglar: /content/finansal-analiz-sistemi/loglar")
```

### Hücre 7 — Raporları ve logları indir (isteğe bağlı)

```python
%cd /content/finansal-analiz-sistemi
!zip -r raporlar.zip raporlar
!zip -r loglar.zip loglar
!zip -r reports_logs.zip raporlar loglar
from google.colab import files
files.download("reports_logs.zip")
```

