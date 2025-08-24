from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Dict, Iterable


def sha256_file(path: str | Path) -> str:
    p = Path(path)
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def list_output_files(root: str | Path) -> list[Path]:
    r = Path(root)
    if not r.exists():
        return []
    return sorted([p for p in r.glob("*.csv") if p.is_file()])


class ArtifactWriter:
    def __init__(self, run_artifacts_dir: str | Path):
        self.dir = Path(run_artifacts_dir)
        self.dir.mkdir(parents=True, exist_ok=True)

    def write_checksums(self, files: Iterable[Path]) -> Path:
        data: Dict[str, str] = {}
        for f in files:
            data[str(f.name)] = sha256_file(f)
        p = self.dir / "checksums.json"
        p.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        return p
