import os
import subprocess
import sys
import glob


def test_cli_emits_logs():
    env = dict(os.environ, LOG_LEVEL="INFO", LOG_FORMAT="json")
    subprocess.run([sys.executable, '-m', 'backtest.cli', 'scan-range', '--config', 'config/colab_config.yaml', '--start', '2025-03-07', '--end', '2025-03-07'], env=env, check=False)
    files = glob.glob('artifacts/logs/app-*.jsonl')
    assert files, 'no log file produced'
