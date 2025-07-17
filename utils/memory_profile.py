"""Context manager that logs peak memory usage.

Using ``with mem_profile():`` appends a ``timestamp,peak,diff`` line to
``reports/memory_profile.csv`` so memory consumption can be reviewed
after execution.
"""

import os
import time
from dataclasses import dataclass, field
from pathlib import Path

import psutil

__all__ = ["mem_profile"]


@dataclass
class mem_profile:
    """Context manager that records peak memory usage to disk."""

    path: Path = field(default_factory=lambda: Path("reports/memory_profile.csv"))

    def __enter__(self):
        """Start tracking process memory usage and return ``self``."""
        self.proc = psutil.Process(os.getpid())
        self.start = self.proc.memory_info().rss
        return self

    def __exit__(self, *exc):
        """Log peak memory usage and allow exception propagation.

        A ``timestamp,peak,diff`` entry is appended to ``self.path``. ``False`` is
        returned so any exception raised inside the ``with`` block is re-raised.
        """
        peak = self.proc.memory_info().rss
        diff = peak - self.start
        self.path.parent.mkdir(exist_ok=True)
        with self.path.open("a") as f:
            f.write(f"{time.time()},{peak},{diff}\n")
        return False
