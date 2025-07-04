from __future__ import annotations

import argparse
from datetime import datetime, timedelta
from pathlib import Path


def purge_old_logs(
    *, log_dir: Path = Path("loglar"), keep_days: int = 7, dry_run: bool = False
) -> int:
    """Purge ``*.log`` and ``*.lock`` files older than ``keep_days`` days.

    Returns the number of matching files (even in dry-run mode).
    """
    cutoff = datetime.now() - timedelta(days=keep_days)
    count = 0
    for f in log_dir.glob("*.log*"):
        if datetime.fromtimestamp(f.stat().st_mtime) < cutoff:
            if dry_run:
                print(f"[DRY-RUN] Would delete {f}")
            else:
                f.unlink()
            count += 1
            lock = f.with_suffix(".lock")
            if lock.exists():
                if dry_run:
                    print(f"[DRY-RUN] Would delete {lock}")
                else:
                    lock.unlink()
                count += 1
    for f in log_dir.glob("*.lock"):
        if (
            not f.with_suffix(".log").exists()
            and datetime.fromtimestamp(f.stat().st_mtime) < cutoff
        ):
            if dry_run:
                print(f"[DRY-RUN] Would delete {f}")
            else:
                f.unlink()
            count += 1
    return count


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Purge old log files.")
    ap.add_argument("--days", type=int, default=7, help="Silinecek log yaşı (gün)")
    ap.add_argument(
        "--dry-run",
        action="store_true",
        help="Dosyaları gerçekten silme, sadece listele",
    )
    args = ap.parse_args()
    n = purge_old_logs(keep_days=args.days, dry_run=args.dry_run)
    print(f"{n} file(s) processed.")
