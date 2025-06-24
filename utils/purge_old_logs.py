from __future__ import annotations

import argparse
from datetime import datetime, timedelta
from pathlib import Path


def purge_old_logs(
    *, log_dir: Path = Path("loglar"), keep_days: int = 7, dry_run: bool = False
) -> int:
    """Purge ``*.log`` files older than ``keep_days`` days in ``log_dir``.

    Returns the number of files considered for deletion.
    """
    cutoff = datetime.now() - timedelta(days=keep_days)
    deleted = 0
    for f in log_dir.glob("*.log"):
        if datetime.fromtimestamp(f.stat().st_mtime) < cutoff:
            if dry_run:
                print(f"[DRY-RUN] Would delete {f}")
            else:
                f.unlink()
            deleted += 1
    return deleted


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
