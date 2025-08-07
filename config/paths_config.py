from __future__ import annotations

from pathlib import Path

# Repository root
_ROOT = Path(__file__).resolve().parent.parent

# Commonly used directories
DATA_PATH = (_ROOT / "Veri").resolve()
OUTPUT_PATH = (_ROOT / "output").resolve()
LOG_DIR = (_ROOT / "logs").resolve()

__all__ = ["DATA_PATH", "OUTPUT_PATH", "LOG_DIR"]
