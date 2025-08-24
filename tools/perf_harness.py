from __future__ import annotations

import argparse
import json
import time
import tracemalloc
from pathlib import Path
import sys

# Allow running as a script without installing the package by
# ensuring the project root is on ``sys.path`` before imports.
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backtest.data.loader import load_prices
from backtest.paths import DATA_DIR


SCENARIOS = {
    "scan-day": lambda symbols, start, end, backend: load_prices(symbols, start, end, backend=backend),
}


def _ensure_parquet_data(symbols, start, end):
    base = DATA_DIR / "parquet"
    for sym in symbols:
        part = base / f"symbol={sym}"
        if not any(part.glob("*.parquet")):
            part.mkdir(parents=True, exist_ok=True)
            import pandas as pd

            dates = pd.date_range(start, end, freq="D")
            if len(dates) == 0:
                dates = pd.to_datetime([start, end])
            df = pd.DataFrame({"Date": dates, "Close": range(1, len(dates) + 1)})
            df.to_parquet(part / f"{sym}.parquet", index=False)

def run_scenario(name: str, backend: str, symbols, start, end) -> dict:
    func = SCENARIOS[name]
    tracemalloc.start()
    t0 = time.perf_counter()
    func(symbols, start, end, backend)
    elapsed = time.perf_counter() - t0
    peak = tracemalloc.get_traced_memory()[1]
    tracemalloc.stop()
    return {"elapsed_sec": elapsed, "peak_kb": peak / 1024.0}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--scenario", required=True)
    ap.add_argument("--backends", required=True)
    ap.add_argument("--start", required=True)
    ap.add_argument("--end", required=True)
    ap.add_argument("--symbols", required=True)
    args = ap.parse_args()
    backends = [b.strip() for b in args.backends.split(",") if b.strip()]
    symbols = [s.strip() for s in args.symbols.split(",") if s.strip()]
    _ensure_parquet_data(symbols, args.start, args.end)
    outdir = Path("artifacts/perf")
    outdir.mkdir(parents=True, exist_ok=True)
    for b in backends:
        stats = run_scenario(args.scenario, b, symbols, args.start, args.end)
        (outdir / f"{b}-{args.scenario}.json").write_text(json.dumps(stats))


if __name__ == "__main__":
    main()
