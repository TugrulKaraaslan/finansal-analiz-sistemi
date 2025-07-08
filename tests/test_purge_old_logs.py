"""Test module for test_purge_old_logs."""

from utils.purge_old_logs import purge_old_logs


def test_purge_dry_run(tmp_path):
    """Test test_purge_dry_run."""
    old = tmp_path / "old.log"
    lock_old = tmp_path / "old.lock"
    old.write_text("")
    old.touch()
    lock_old.touch()
    new = tmp_path / "new.log"
    new.write_text("")
    import os
    import time

    os.utime(old, (time.time() - 864000,) * 2)  # 10 gün
    deleted = purge_old_logs(log_dir=tmp_path, keep_days=7, dry_run=True)
    assert deleted == 2 and old.exists() and lock_old.exists() and new.exists()
