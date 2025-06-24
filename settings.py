import os

import yaml

_cfg_path = os.path.join(os.path.dirname(__file__), "settings.yaml")
if os.path.exists(_cfg_path):
    with open(_cfg_path) as f:
        _cfg = yaml.safe_load(f) or {}
else:
    _cfg = {}

MAX_FILTER_DEPTH = _cfg.get("max_filter_depth", 5)
