import psutil
import os
import time


class mem_profile:
    def __enter__(self):
        self.proc = psutil.Process(os.getpid())
        self.start = self.proc.memory_info().rss

    def __exit__(self, *exc):
        peak = self.proc.memory_info().rss
        os.makedirs("reports", exist_ok=True)
        with open("reports/memory_profile.csv", "a") as f:
            f.write(f"{time.time()},{peak}\n")
