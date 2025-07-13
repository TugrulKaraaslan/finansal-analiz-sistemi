"""Context manager that logs memory usage to ``reports/memory_profile.csv``.

Usage example::

    with mem_profile():
        ...  # run memory intensive task

Each invocation appends a ``timestamp,peak,diff`` line to the CSV file.
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
        """Write memory usage delta to CSV and propagate exceptions.

        Returns:
            bool: Always ``False`` so that exceptions bubble up.
        """
        peak = self.proc.memory_info().rss
        diff = peak - self.start
        os.makedirs("reports", exist_ok=True)
        with open("reports/memory_profile.csv", "a") as f:
            f.write(f"{time.time()},{peak},{diff}\n")
        return False
