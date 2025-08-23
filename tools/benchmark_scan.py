from __future__ import annotations
from time import perf_counter
import json, subprocess, sys, os
from pathlib import Path

CMD = [sys.executable, '-m', 'backtest.cli', 'scan-range',
       '--config', 'config/colab_config.yaml',
       '--start', '2025-03-07', '--end', '2025-03-09']

def main():
    Path('artifacts/bench').mkdir(parents=True, exist_ok=True)
    t0 = perf_counter()
    res = subprocess.run(CMD, capture_output=True, text=True)
    dt = perf_counter() - t0
    out = {
        'cmd': ' '.join(CMD),
        'returncode': res.returncode,
        'wall_time_sec': dt,
        'stdout_tail': res.stdout[-500:],
        'stderr_tail': res.stderr[-500:],
    }
    Path('artifacts/bench/scan_bench.json').write_text(json.dumps(out, indent=2), encoding='utf-8')
    print(json.dumps(out, indent=2))
    sys.exit(res.returncode)

if __name__ == '__main__':
    main()
