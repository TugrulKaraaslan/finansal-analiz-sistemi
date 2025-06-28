#!/usr/bin/env bash
pip install --quiet pip-tools
pip-compile --output-file=requirements.lock requirements.txt
echo "✅  Requirements locked."
