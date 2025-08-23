import tracemalloc, json
from pathlib import Path
import subprocess, sys

Path('artifacts/memory').mkdir(parents=True, exist_ok=True)
tracemalloc.start()
subprocess.run([sys.executable, '-m', 'backtest.cli', 'scan-range',
                '--config', 'config/colab_config.yaml',
                '--start', '2025-03-07', '--end', '2025-03-09'], check=False)
snapshot = tracemalloc.take_snapshot()
stats = snapshot.statistics('lineno')[:50]
rec = [{
    'trace': str(s.traceback[0]),
    'size_kb': round(s.size/1024, 2),
    'count': s.count,
} for s in stats]
Path('artifacts/memory/top50.json').write_text(json.dumps(rec, indent=2), encoding='utf-8')
print('memory snapshot written: artifacts/memory/top50.json')
