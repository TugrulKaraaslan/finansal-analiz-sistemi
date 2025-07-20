"""Tests for the ``purge_old_logs`` maintenance helper.

The module should correctly identify old log and lock files, deleting them
when not running in dry-run mode.
"""

import pytest

from utils.purge_old_logs import purge_old_logs


def test_purge_dry_run(tmp_path):
    """Dry-run should count deletable files without removing them."""
    old = tmp_path / "old.log"
    lock_old = tmp_path / "old.lock"
    old.write_text("")
    old.touch()
    lock_old.touch()
    new = tmp_path / "new.log"
    new.write_text("")
    import os
    import time

    os.utime(old, (time.time() - 864000,) * 2)  # 10 days ago
    deleted = purge_old_logs(log_dir=tmp_path, keep_days=7, dry_run=True)
    assert deleted == 2 and old.exists() and lock_old.exists() and new.exists()


def test_custom_patterns(tmp_path):
    """Files matching custom patterns should be removed."""
    old_txt = tmp_path / "old.txt"
    old_txt.write_text("x")
    import os
    import time

    os.utime(old_txt, (time.time() - 864000,) * 2)
    removed = purge_old_logs(log_dir=tmp_path, keep_days=7, patterns=("*.txt",))
    assert removed == 1
    assert not old_txt.exists()


def test_negative_keep_days_raises(tmp_path):
    """Negative ``keep_days`` should trigger ``ValueError``."""
    with pytest.raises(ValueError):
        purge_old_logs(log_dir=tmp_path, keep_days=-1)


def test_patterns_as_string(tmp_path):
    """A single pattern string should be accepted."""
    log = tmp_path / "foo.log"
    log.write_text("x")
    import os
    import time

    os.utime(log, (time.time() - 864000,) * 2)
    removed = purge_old_logs(log_dir=tmp_path, keep_days=7, patterns="*.log")
    assert removed == 1
    assert not log.exists()


def test_missing_directory_returns_zero(tmp_path):
    """Nonexistent ``log_dir`` should be handled gracefully."""
    missing = tmp_path / "missing"
    assert purge_old_logs(log_dir=missing, keep_days=7) == 0


def test_log_dir_must_be_directory(tmp_path):
    """``log_dir`` pointing to a file should raise ``NotADirectoryError``."""
    file_path = tmp_path / "some.log"
    file_path.write_text("x")
    with pytest.raises(NotADirectoryError):
        purge_old_logs(log_dir=file_path, keep_days=7)
