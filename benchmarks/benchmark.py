"""Measure CPU throughput by summing random integers.

The benchmark generates one million numbers, sums them and writes the
elapsed time to ``benchmark_output.txt``.
"""

import random
import time


def run_bench() -> float:
    """Run the integer-summing loop and report the runtime.

    Returns:
        float: Execution time in seconds.
    """
    start = time.perf_counter()
    _ = sum(random.randint(1, 100) for _ in range(1_000_000))
    duration = time.perf_counter() - start
    print(f"Benchmark Sonucu: {duration:.4f} saniye")
    with open("benchmarks/benchmark_output.txt", "w") as f:
        f.write(f"{duration:.4f}\n")
    return duration


if __name__ == "__main__":
    run_bench()
