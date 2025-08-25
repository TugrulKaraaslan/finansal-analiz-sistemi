from __future__ import annotations

from pathlib import Path


def normalize_path(base: Path, p: str | Path) -> Path:
    """Return absolute path for *p* relative to *base*.

    ``p`` may be absolute, relative, or contain ``~``. The path is not
    required to exist. ``base`` should be the directory of the config file.
    """

    q = Path(p).expanduser()
    if not q.is_absolute():
        q = base / q
    return q.resolve()
