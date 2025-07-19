"""Context manager to record peak memory usage.

Using ``with mem_profile():`` appends a ``timestamp,peak,diff`` line to
``reports/memory_profile.csv`` so memory consumption can be reviewed
after execution.  The ``MemoryProfile`` class provides the actual
implementation while ``mem_profile`` is kept as a backwards compatible
alias.
"""

import os
import time
from dataclasses import dataclass, field
from pathlib import Path

import psutil

__all__ = ["MemoryProfile", "mem_profile"]


@dataclass
class MemoryProfile:
    """Context manager that records peak memory usage to disk."""

    path: Path = field(default_factory=lambda: Path("reports/memory_profile.csv"))
    proc: psutil.Process = field(init=False)
    start: int = field(init=False)

    def __enter__(self) -> "MemoryProfile":
        """Start tracking process memory usage and return ``self``."""
        self.proc = psutil.Process(os.getpid())
        self.start = self.proc.memory_info().rss
        return self

    def __exit__(self, exc_type, exc, tb) -> bool:
        """Log peak memory usage and allow exception propagation."""
        peak = self.proc.memory_info().rss
        diff = peak - self.start
        self.path.parent.mkdir(exist_ok=True)
        with self.path.open("a", encoding="utf-8") as f:
            f.write(f"{time.time()},{peak},{diff}\n")
        return False


mem_profile = MemoryProfile
