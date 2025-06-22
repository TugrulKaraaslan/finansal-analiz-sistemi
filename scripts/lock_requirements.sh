#!/usr/bin/env bash
pip install --quiet pip-tools
pip-compile requirements.in
echo "✅  Requirements locked."
