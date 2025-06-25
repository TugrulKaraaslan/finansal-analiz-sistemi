import os, time, pytest
from pathlib import Path

from utils.log_cleaner import purge_old_logs


@pytest.mark.parametrize("dry_run", [True, False])
def test_purge_old_logs(tmp_path: Path, dry_run: bool):
    old = tmp_path / "old.log"
    new = tmp_path / "new.log"

    old.write_text("x")
    new.write_text("y")

    # 10 gün geriye çek
    old_time = time.time() - 10 * 86400
    os.utime(old, (old_time, old_time))

    removed = purge_old_logs(tmp_path, days=7, dry_run=dry_run)

    assert removed == (0 if dry_run else 1)
    assert new.exists()
    assert old.exists() is dry_run
