from utils.purge_old_logs import purge_old_logs


def test_purge_dry_run(tmp_path):
    old = tmp_path / "old.log"
    old.write_text("")
    old.touch()
    new = tmp_path / "new.log"
    new.write_text("")
    import os
    import time

    os.utime(old, (time.time() - 864000,) * 2)  # 10 gün
    deleted = purge_old_logs(log_dir=tmp_path, keep_days=7, dry_run=True)
    assert deleted == 1 and old.exists() and new.exists()
