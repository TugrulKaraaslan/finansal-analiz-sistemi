"""Context manager that logs peak memory usage.

Using ``with mem_profile():`` appends ``timestamp,peak,diff`` rows to
``reports/memory_profile.csv`` for later analysis.
"""

import os
import time

import psutil


class mem_profile:
    """Context manager that records peak memory usage to disk."""

    def __enter__(self):
        """Start tracking process memory usage and return ``self``."""
        self.proc = psutil.Process(os.getpid())
        self.start = self.proc.memory_info().rss
        return self

    def __exit__(self, *exc):
        """Log peak memory usage and allow exception propagation.

        A ``timestamp,peak,diff`` entry is appended to
        ``reports/memory_profile.csv``. ``False`` is returned so any
        exception raised inside the ``with`` block is re-raised.
        """
        peak = self.proc.memory_info().rss
        diff = peak - self.start
        os.makedirs("reports", exist_ok=True)
        with open("reports/memory_profile.csv", "a") as f:
            f.write(f"{time.time()},{peak},{diff}\n")
        return False
