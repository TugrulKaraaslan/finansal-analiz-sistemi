#!/usr/bin/env bash
set -euo pipefail
export PYTHONUNBUFFERED=1

echo "== Env =="
python --version
pip --version

echo "== Legacy CSV guard =="
pat='(filters\.csv|load_filters_csv|read_filters_csv|--filters(\s|=)|--filters-off)'
repo_root="$(git rev-parse --show-toplevel)"
if rg -n "$pat" -S "$repo_root" --glob '!tools/legacy/**' --glob '!tools/ci_checks.sh'; then
  echo -e "\e[31mCSV/legacy flags detected\e[0m"; exit 1; fi

echo "== Ensure package importable =="
python - <<'PY'
import importlib, sys
m = importlib.import_module("backtest")
print("backtest package OK:", m.__file__)
PY

echo "== CLI help smoke =="
if ! python -m backtest.cli -h >/dev/null 2>&1; then
  echo "ERR: cli help failed"
  python - <<'PY'
import traceback
try:
    import backtest.cli as cli
    print("Imported backtest.cli OK but -h exited nonzero")
except Exception:
    traceback.print_exc()
    raise
PY
  exit 1
fi

echo "== Pytest =="
pytest -q
