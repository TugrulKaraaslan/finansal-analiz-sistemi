"""Verify log cleanup utilities remove outdated files.

The ``purge_old_logs`` helper should delete aged log entries while leaving
recent ones intact, supporting optional dry-run mode.
"""

import os
import time
from pathlib import Path

import pytest

from utils.purge_old_logs import purge_old_logs


@pytest.mark.parametrize("dry_run", [True, False])
def test_purge_old_logs(tmp_path: Path, dry_run: bool):
    """Old log files should be purged while newer ones remain."""
    old = tmp_path / "old.log"
    new = tmp_path / "new.log"
    lock_old = tmp_path / "old.lock"

    old.write_text("x")
    new.write_text("y")
    lock_old.write_text("")

    # rewind timestamps by 10 days
    old_time = time.time() - 10 * 86400
    os.utime(old, (old_time, old_time))

    removed = purge_old_logs(log_dir=tmp_path, keep_days=7, dry_run=dry_run)

    assert removed == 2
    if not dry_run:
        assert not old.exists()
        assert not lock_old.exists()
    else:
        assert old.exists()
        assert lock_old.exists()
    assert new.exists()
    assert old.exists() is dry_run
    assert lock_old.exists() is dry_run
