#!/usr/bin/env bash
set -Eeuo pipefail

# 1. Tek kaynak doğrulaması (veri_guncel_fix)
if grep -RIn "veri_guncel_fix" backtest utils tools tests | grep -v "tools/ci_checks.sh" >/dev/null; then
  echo "ERR: legacy path 'veri_guncel_fix' detected" >&2
  exit 1
fi

# 2. Dış indirme guard'ı
if grep -RIn "requests\|http://\|https://\|wget\|urllib" backtest utils tools | grep -v "backtest/downloader" >/dev/null; then
  echo "ERR: network call outside downloader" >&2
  exit 1
fi

# 3. CLI yardım çıktısı kontrolü
python -m backtest.cli --help >/dev/null 2>&1 || { echo "ERR: cli help failed" >&2; exit 1; }

# 4. Pytest (offline)
export ALLOW_DOWNLOAD=0
pytest -q || { echo "ERR: pytest failed" >&2; exit 1; }

# 5. Markdown hızlı denetim (opsiyonel, ağsız)
python <<'PY'
import sys, re, pathlib
files = [pathlib.Path('README.md'), pathlib.Path('README_STAGE1.md'), pathlib.Path('USAGE.md'), pathlib.Path('TROUBLESHOOT.md'), pathlib.Path('FAQ.md')]
pattern = re.compile(r'\[[^\]]+\]\((?!https?://)[^)]+\)')
missing = []
for f in files:
    text = f.read_text(encoding='utf-8')
    if not pattern.search(text):
        missing.append(f)
if missing:
    for f in missing:
        print(f"ERR: no relative link found in {f}", file=sys.stderr)
    sys.exit(1)
PY

echo "OK: offline default & data/ single-source checks passed"
