#!/usr/bin/env bash
set -Eeuo pipefail

bash "$(dirname "$0")/../ci_checks.sh"
python -m backtest.cli --help >/dev/null 2>&1
pytest -q
echo "dry run OK"
