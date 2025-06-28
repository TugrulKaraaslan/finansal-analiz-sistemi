#!/usr/bin/env bash
pip install --quiet pip-tools
pip-compile --output-file=requirements.lock requirements.in
echo "✅  Requirements locked."
