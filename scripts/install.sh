#!/usr/bin/env bash
# Simple installer to set up dependencies for development, CI and Colab
set -e

PYTHON=${PYTHON:-python}

# determine base requirements file
echo "Checking for Google Colab environment..."
if $PYTHON - <<'PY'
import importlib.util, sys
try:
    importlib.util.find_spec('google.colab')
    sys.exit(0)
except ModuleNotFoundError:
    sys.exit(1)
PY
then
    BASE="requirements-colab.txt"
    echo "Colab detected -> using $BASE"
else
    BASE="requirements.txt"
    echo "Standard environment -> using $BASE"
fi

$PYTHON -m pip install --upgrade pip
$PYTHON -m pip install -r "$BASE"
$PYTHON -m pip install -r requirements-dev.txt
# openbb wrapper for technical analysis
$PYTHON -m pip install pandas-ta-openbb

echo "Dependencies installed."
