import random
import time


def run_bench():
    start = time.perf_counter()
    total = 0
    for _ in range(1000000):
        total += random.randint(1, 100)
    duration = time.perf_counter() - start
    print(f"Benchmark Sonucu: {duration:.4f} saniye")
    with open("benchmarks/benchmark_output.txt", "w") as f:
        f.write(f"{duration:.4f}\n")
    return duration


if __name__ == "__main__":
    run_bench()
