"""Context manager to log memory usage during execution."""

import os
import time

import psutil


class mem_profile:
    """Write peak memory usage to ``reports/memory_profile.csv``."""

    def __enter__(self):
        """Start tracking process memory usage."""
        self.proc = psutil.Process(os.getpid())
        self.start = self.proc.memory_info().rss
        return self

    def __exit__(self, *exc):
        """Write memory usage delta to CSV on exit."""
        peak = self.proc.memory_info().rss
        diff = peak - self.start
        os.makedirs("reports", exist_ok=True)
        with open("reports/memory_profile.csv", "a") as f:
            f.write(f"{time.time()},{peak},{diff}\n")
        return False
