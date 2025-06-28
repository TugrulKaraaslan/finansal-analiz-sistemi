import os

import yaml

_cfg_path = os.path.join(os.path.dirname(__file__), "settings.yaml")
if os.path.exists(_cfg_path):
    with open(_cfg_path) as f:
        _cfg = yaml.safe_load(f) or {}
else:
    _cfg = {}

try:
    MAX_FILTER_DEPTH = int(_cfg.get("max_filter_depth", 7))
except (TypeError, ValueError):
    MAX_FILTER_DEPTH = 7
