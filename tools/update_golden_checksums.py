from __future__ import annotations

import hashlib
import json
import os
import sys
import time
from pathlib import Path

import yaml


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for ch in iter(lambda: f.read(65536), b""):
            h.update(ch)
    return h.hexdigest()


MANIFEST = Path("tests/golden/manifest.yaml")
OUT = Path("tests/golden/checksums.json")


def _collect_from_manifest() -> list[Path]:
    if not MANIFEST.exists():
        return []
    cfg = yaml.safe_load(MANIFEST.read_text()) or {}
    out: list[Path] = []
    for rel in cfg.get("files") or []:
        p = Path(rel)
        if p.exists():
            out.append(p)
    for rule in cfg.get("pick_latest") or []:
        base = Path(rule["path"])
        if not base.exists():
            continue
        pats = list(base.glob(rule.get("pattern", "*")))
        pats = [p for p in pats if p.is_file()]
        pats.sort()  # testlerde alfabetik sıralama kullanılıyor
        cnt = int(rule.get("count", 2))
        out.extend(pats[-cnt:])
    # uniq & stable order
    uniq = []
    seen = set()
    for p in out:
        s = str(p)
        if s not in seen:
            uniq.append(Path(s))
            seen.add(s)
    return uniq


def main(write: bool = True):
    files = _collect_from_manifest()
    data = {str(p): sha256(p) for p in files if p.exists()}
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
    print(f"Wrote {len(data)} golden checksums → {OUT}")


if __name__ == "__main__":
    main(True)
