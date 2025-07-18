"""Delete aged log files from a directory.

Files older than ``keep_days`` are removed. By default the ``loglar``
folder under the project root is targeted. When ``dry_run`` is ``True``
the function only prints which files would be deleted. The helper is
resilient against concurrent deletions and silently ignores missing
files encountered during scanning.
"""

from __future__ import annotations

import argparse
from collections.abc import Iterable
from datetime import datetime, timedelta
from pathlib import Path


def purge_old_logs(
    *,
    log_dir: Path | None = None,
    keep_days: int = 7,
    dry_run: bool = False,
    patterns: Iterable[str] | None = None,
) -> int:
    """Remove old log files from ``log_dir``.

    Files matching ``patterns`` (``*.log*`` by default) and orphan ``*.lock``
    entries older than ``keep_days`` days are deleted. When ``dry_run`` is
    ``True`` the function only prints which files would be removed.

    Args:
        log_dir (Path | None, optional): Directory containing log files.
            ``None`` defaults to ``loglar``.
        keep_days (int, optional): Files modified more than this many days ago
            are removed.
        dry_run (bool, optional): When ``True`` only print what would be
            deleted.
        patterns (Iterable[str] | None, optional): Glob patterns for log
            files. Defaults to ``("*.log*",)``.

    Raises:
        ValueError: If ``keep_days`` is negative.

    Returns:
        int: Number of files processed (also when ``dry_run`` is ``True``).

    """
    if keep_days < 0:
        raise ValueError("keep_days must be non-negative")

    log_dir = Path("loglar") if log_dir is None else Path(log_dir)
    patterns = ("*.log*",) if patterns is None else tuple(patterns)

    cutoff_ts = (datetime.now() - timedelta(days=keep_days)).timestamp()
    count = 0

    def remove(path: Path) -> None:
        if dry_run:
            print(f"[DRY-RUN] Would delete {path}")
        else:
            path.unlink(missing_ok=True)

    def is_expired(p: Path) -> bool:
        """Return ``True`` when ``p`` is older than the cutoff timestamp."""
        try:
            return p.stat().st_mtime < cutoff_ts
        except FileNotFoundError:  # pragma: no cover - race condition
            return False

    for pat in patterns:
        for log_file in log_dir.glob(pat):
            if is_expired(log_file):
                remove(log_file)
                count += 1
                lock = log_file.with_suffix(".lock")
                if lock.exists():
                    remove(lock)
                    count += 1

    for lock_file in log_dir.glob("*.lock"):
        if not lock_file.with_suffix(".log").exists() and is_expired(lock_file):
            remove(lock_file)
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
