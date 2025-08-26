import os
import sys
from pathlib import Path

import pandas as pd

sys.path.append(str(Path(__file__).resolve().parent.parent))
from backtest.filters.preflight import validate_filters  # noqa: E402
from backtest.paths import DATA_DIR  # noqa: E402
from filters.module_loader import load_filters_from_module  # noqa: E402

alias_mode = os.getenv("PREFLIGHT_ALIAS_MODE", "forbid")
allow_unknown = os.getenv("PREFLIGHT_ALLOW_UNKNOWN", "0") == "1"
filters_module = os.getenv("FILTERS_MODULE")

filters_df = load_filters_from_module(filters_module)
sample = next(DATA_DIR.rglob("*.xlsx"))
dataset_df = pd.read_excel(sample, nrows=0)

validate_filters(
    filters_df,
    dataset_df,
    alias_mode=alias_mode,
    allow_unknown=allow_unknown,
)
print(f"preflight ok (alias_mode={alias_mode}, allow_unknown={allow_unknown})")
