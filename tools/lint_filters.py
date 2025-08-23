from __future__ import annotations

"""Utility script to lint filter files.

This script loads the project configuration and determines the Excel
directory used by tests. The location can be overridden via the
``EXCEL_DIR`` environment variable which is useful in CI where fixtures are
generated at runtime.
"""

from pathlib import Path
import os
import sys
import yaml


def _load_cfg(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def main() -> None:
    cfg_path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("config_scan.yml")
    cfg = _load_cfg(cfg_path)

    # mevcut cfg okuma mantığının üstüne ENV override ekle
    excel_dir = Path(os.getenv("EXCEL_DIR", cfg["data"]["excel_dir"]))
    print(f"Using excel_dir={excel_dir}")


if __name__ == "__main__":  # pragma: no cover
    main()

