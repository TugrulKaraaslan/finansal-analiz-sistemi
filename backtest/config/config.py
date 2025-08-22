from __future__ import annotations
from pathlib import Path
from typing import Any, Dict

try:
    import yaml
except Exception:  # yaml yoksa minik parser yerine hata verelim
    yaml = None

_DEFAULT = {
    "cli": {"log_level": "INFO"},
    "flags": {"dry_run": True, "filters_enabled": True, "write_outputs": True},
    "paths": {"outputs": "raporlar/gunluk", "logs": "logs", "artifacts": "artifacts"},
}


def load_config(path: str | None) -> Dict[str, Any]:
    cfg = {**_DEFAULT}
    if not path:
        return cfg
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"config bulunamadı: {p}")
    if yaml is None:
        raise RuntimeError("PyYAML gerekli: 'pip install pyyaml'")
    with p.open("r", encoding="utf-8") as f:
        doc = yaml.safe_load(f) or {}
    # shallow merge
    for k in doc:
        if isinstance(doc[k], dict) and k in cfg:
            cfg[k].update(doc[k])
        else:
            cfg[k] = doc[k]
    return cfg


def merge_cli_overrides(cfg: Dict[str, Any], **overrides) -> Dict[str, Any]:
    out = {**cfg}
    # flags altındaki override'ları işle
    flags = {**cfg.get("flags", {})}
    for k, v in overrides.items():
        if v is None:
            continue
        if k in ("dry_run", "filters_enabled", "write_outputs"):
            flags[k] = bool(v)
    out["flags"] = flags
    # cli log_level
    if "log_level" in overrides and overrides["log_level"]:
        out.setdefault("cli", {})["log_level"] = overrides["log_level"]
    return out
