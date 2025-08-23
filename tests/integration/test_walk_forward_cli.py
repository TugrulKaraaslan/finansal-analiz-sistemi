import os
import subprocess
import sys
from pathlib import Path


def test_walk_forward_smoke():
    env = dict(
        **os.environ,
        WF_START="2025-03-07",
        WF_END="2025-03-11",
        WF_TRAIN_DAYS="2",
        WF_TEST_DAYS="1",
        WF_STEP_DAYS="1",
        WF_SKIP_SCAN="1",
    )
    res = subprocess.run(
        [sys.executable, "tools/walk_forward_eval.py"],
        env=env,
        capture_output=True,
        text=True,
    )
    assert res.returncode == 0, res.stderr[-400:]
    assert Path("artifacts/wf/summary.json").exists()
