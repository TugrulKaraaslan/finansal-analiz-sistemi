from pathlib import Path
import os
import sys

sys.path.append(str(Path(__file__).resolve().parent.parent))
from backtest.paths import EXCEL_DIR
from backtest.filters.preflight import validate_filters

filters = Path("filters.csv") if Path("filters.csv").exists() else Path("config/filters.csv")
fail_on_alias = os.getenv("PREFLIGHT_FAIL_ON_ALIAS", "1") == "1"
allow_unknown = os.getenv("PREFLIGHT_ALLOW_UNKNOWN", "0") == "1"

validate_filters(filters, EXCEL_DIR, fail_on_alias=fail_on_alias, allow_unknown=allow_unknown)
print(f"preflight ok (fail_on_alias={fail_on_alias}, allow_unknown={allow_unknown})")
