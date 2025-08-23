from pathlib import Path
import os
import sys

sys.path.append(str(Path(__file__).resolve().parent.parent))
from backtest.paths import EXCEL_DIR  # noqa: E402
from backtest.filters.preflight import validate_filters  # noqa: E402

filters = Path("filters.csv")
if not filters.exists():
    filters = Path("config/filters.csv")
alias_mode = os.getenv("PREFLIGHT_ALIAS_MODE", "allow")
allow_unknown = os.getenv("PREFLIGHT_ALLOW_UNKNOWN", "0") == "1"

validate_filters(
    filters,
    EXCEL_DIR,
    alias_mode=alias_mode,
    allow_unknown=allow_unknown,
)
print(f"preflight ok (alias_mode={alias_mode}, allow_unknown={allow_unknown})")
