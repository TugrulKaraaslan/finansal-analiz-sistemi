#!/usr/bin/env bash
set -euo pipefail
export PYTHONUNBUFFERED=1

echo "== Env =="
python --version
pip --version

echo "== Legacy CSV guard =="
p1="load_filters_"'csv'
p2="--filt"'ers\\b'
p3="--filt"'ers-off'
pat="${p1}|${p2}|${p3}"
if rg -n "$pat" -S tools -g '!ci_checks.sh'; then
  echo "CSV/legacy flags detected"; exit 1; fi

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
