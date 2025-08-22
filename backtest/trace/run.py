from __future__ import annotations
import os
import json
import logging
import platform
import subprocess
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

LOGGER = logging.getLogger("backtest.trace")


def new_run_id() -> str:
    ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    # 8 char kısa rastgele: os.urandom(4).hex()
    rid = f"{ts}_{os.urandom(4).hex()}"
    return rid


def _git_short_hash() -> str | None:
    try:
        out = subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], stderr=subprocess.DEVNULL)
        return out.decode().strip()
    except Exception:
        return None


def _package_versions() -> Dict[str, str]:
    vers: Dict[str, str] = {}
    try:
        import pandas as pd  # type: ignore
        vers["pandas"] = getattr(pd, "__version__", "?")
    except Exception:
        pass
    try:
        import numpy as np  # type: ignore
        vers["numpy"] = getattr(np, "__version__", "?")
    except Exception:
        pass
    return vers


@dataclass
class RunContext:
    run_id: str
    logs_dir: Path
    artifacts_dir: Path

    @classmethod
    def create(cls, logs_root: str | os.PathLike, artifacts_root: str | os.PathLike) -> "RunContext":
        rid = new_run_id()
        logs_dir = Path(logs_root)
        arts_root = Path(artifacts_root)
        logs_dir.mkdir(parents=True, exist_ok=True)
        # artefakt alt klasörü run_id bazlı
        art_dir = arts_root / rid
        art_dir.mkdir(parents=True, exist_ok=True)
        return cls(run_id=rid, logs_dir=logs_dir, artifacts_dir=art_dir)

    def write_env_snapshot(self) -> Path:
        env = {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "git": _git_short_hash(),
            "packages": _package_versions(),
        }
        p = self.artifacts_dir / "env.json"
        p.write_text(json.dumps(env, ensure_ascii=False, indent=2), encoding="utf-8")
        LOGGER.info("env.json yazıldı: %s", p)
        return p

    def write_config_snapshot(self, config: Dict[str, Any], inputs: Dict[str, Any]) -> None:
        cfgp = self.artifacts_dir / "config.json"
        inpp = self.artifacts_dir / "inputs.json"
        cfgp.write_text(json.dumps(config, ensure_ascii=False, indent=2), encoding="utf-8")
        inpp.write_text(json.dumps(inputs, ensure_ascii=False, indent=2), encoding="utf-8")
        LOGGER.info("config.json ve inputs.json yazıldı")
