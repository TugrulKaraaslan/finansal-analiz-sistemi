import hashlib
import json
from pathlib import Path


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_artifacts_checksum():
    data = json.loads(Path("tests/golden/checksums.json").read_text())
    for rel, expected in data.items():
        p = Path(rel)
        assert p.exists(), f"Missing artifact {rel}"
        assert _sha256(p) == expected
