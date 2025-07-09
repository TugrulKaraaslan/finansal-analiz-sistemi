"""Minimal benchmark module for timing a basic summation loop."""

import random
import time


def run_bench() -> float:
    """Return the runtime of a dummy integer summation loop."""
    start = time.perf_counter()
    _ = sum(random.randint(1, 100) for _ in range(1_000_000))
    duration = time.perf_counter() - start
    print(f"Benchmark Sonucu: {duration:.4f} saniye")
    with open("benchmarks/benchmark_output.txt", "w") as f:
        f.write(f"{duration:.4f}\n")
    return duration


if __name__ == "__main__":
    run_bench()
