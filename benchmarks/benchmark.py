"""Simple benchmark for evaluating loop performance."""

import random
import time


def run_bench() -> float:
    """Return runtime for a simple integer summation loop."""
    start = time.perf_counter()
    # intentionally compute a meaningless sum to keep the loop workload
    _ = sum(random.randint(1, 100) for _ in range(1_000_000))
    duration = time.perf_counter() - start
    print(f"Benchmark Sonucu: {duration:.4f} saniye")
    with open("benchmarks/benchmark_output.txt", "w") as f:
        f.write(f"{duration:.4f}\n")
    return duration


if __name__ == "__main__":
    run_bench()
