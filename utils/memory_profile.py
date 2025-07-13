"""Context manager to log peak memory usage in bytes.

Use ``with mem_profile():`` to append ``timestamp,peak,diff`` entries to
``reports/memory_profile.csv`` so memory trends can be reviewed later.
"""

import os
import time

import psutil


class mem_profile:
    """Track peak memory usage within a ``with`` block."""

    def __enter__(self):
        """Start tracking process memory usage and return ``self``."""
        self.proc = psutil.Process(os.getpid())
        self.start = self.proc.memory_info().rss
        return self

    def __exit__(self, *exc):
        """Log the peak memory delta to ``reports/memory_profile.csv``.

        Returns:
            bool: Always ``False`` so that any exception is re-raised.
        """
        peak = self.proc.memory_info().rss
        diff = peak - self.start
        os.makedirs("reports", exist_ok=True)
        with open("reports/memory_profile.csv", "a") as f:
            f.write(f"{time.time()},{peak},{diff}\n")
        return False
