import os
import subprocess
import sys
from pathlib import Path


def test_from_to_rejected():
    env = dict(os.environ, PYTHONPATH=str(Path(__file__).resolve().parents[2]))
    p = subprocess.run(
        [sys.executable, '-m', 'backtest.cli', 'scan-range', '--from', '2025-03-07'],
        capture_output=True,
        env=env,
    )
    assert p.returncode != 0
    assert b'unrecognized arguments' in p.stderr


def test_start_end_ok(tmp_path):
    (tmp_path / 'filters.csv').write_text(
        'FilterCode;PythonQuery\nF1;close>1\n', encoding='utf-8'
    )
    env = dict(os.environ, PYTHONPATH=str(Path(__file__).resolve().parents[2]))
    p = subprocess.run(
        [
            sys.executable,
            '-m',
            'backtest.cli',
            'scan-range',
            '--start',
            '2025-03-07',
            '--end',
            '2025-03-08',
            '--help',
        ],
        cwd=tmp_path,
        capture_output=True,
        env=env,
    )
    assert p.returncode == 0
