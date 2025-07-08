"""Convenience wrapper around :mod:`run` for CLI use and imports."""

from __future__ import annotations

import runpy
import sys
from pathlib import Path


def _ensure_project_root() -> None:
    """Add the project root directory to ``sys.path`` if missing."""
    project_root = Path(__file__).resolve().parents[1]
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))


_ensure_project_root()

# Re-export frequently used helpers from ``run.py`` so tests and users can simply
# ``import finansal_analiz_sistemi.main``.
from run import calistir_tum_sistemi, run_pipeline  # noqa: E402

__all__ = ["calistir_tum_sistemi", "run_pipeline"]


if __name__ == "__main__":  # pragma: no cover - manual entry point
    runpy.run_module("run", run_name="__main__")
