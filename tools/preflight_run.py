import os
import sys
from pathlib import Path

import pandas as pd

sys.path.append(str(Path(__file__).resolve().parent.parent))
from backtest.filters.preflight import validate_filters  # noqa: E402
from backtest.paths import DATA_DIR  # noqa: E402
from io_filters import read_filters_file  # noqa: E402

filters_path = Path("filters.csv")
if not filters_path.exists():
    filters_path = Path("config/filters.csv")
alias_mode = os.getenv("PREFLIGHT_ALIAS_MODE", "forbid")
allow_unknown = os.getenv("PREFLIGHT_ALLOW_UNKNOWN", "0") == "1"

filters_df = read_filters_file(filters_path)
sample = next(DATA_DIR.rglob("*.xlsx"))
dataset_df = pd.read_excel(sample, nrows=0)

validate_filters(
    filters_df,
    dataset_df,
    alias_mode=alias_mode,
    allow_unknown=allow_unknown,
)
print(f"preflight ok (alias_mode={alias_mode}, allow_unknown={allow_unknown})")
