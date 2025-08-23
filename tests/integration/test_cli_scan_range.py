import subprocess
import sys

def test_scan_range_smoke():
    cmd = [sys.executable, '-m', 'backtest.cli', 'scan-range',
           '--config', 'config/colab_config.yaml',
           '--start', '2025-03-07', '--end', '2025-03-09']
    res = subprocess.run(cmd, capture_output=True, text=True)
    assert res.returncode == 0, res.stderr[:300]
