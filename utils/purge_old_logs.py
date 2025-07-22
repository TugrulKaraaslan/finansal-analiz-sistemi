"""Delete aged log files from a directory.

Files older than ``keep_days`` are removed. By default the ``loglar``
folder located next to this module is targeted. When ``dry_run`` is ``True``
the function only prints which files would be deleted. The helper is
resilient against concurrent deletions and silently ignores missing
files encountered during scanning.
"""

from __future__ import annotations

__all__ = ["purge_old_logs"]

import argparse
import logging
from collections.abc import Iterable
from datetime import datetime, timedelta
from pathlib import Path


def purge_old_logs(
    *,
    log_dir: Path | None = None,
    keep_days: int = 7,
    dry_run: bool = False,
    patterns: Iterable[str] | str | None = None,
    logger: logging.Logger | None = None,
) -> int:
    """Remove old log files from ``log_dir``.

    Files matching ``patterns`` (``*.log*`` by default) and orphan ``*.lock``
    entries older than ``keep_days`` days are deleted. ``patterns`` may be a
    single glob string or an iterable of patterns. When ``dry_run`` is ``True``
    the function only prints which files would be removed. If ``log_dir`` does
    not exist the function returns ``0`` without raising an error.

    Args:
        log_dir (Path | None, optional): Directory containing log files.
            ``None`` defaults to ``loglar``.
        keep_days (int, optional): Files modified more than this many days ago
            are removed.
        dry_run (bool, optional): When ``True`` only print what would be
            deleted.
        patterns (Iterable[str] | str | None, optional): Glob pattern(s) for log
            files. Defaults to ``("*.log*",)``.
        logger (logging.Logger | None, optional): Logger used for informational
            messages. ``None`` falls back to ``print`` when ``dry_run`` is
            enabled.

    Raises:
        ValueError: If ``keep_days`` is negative.
        NotADirectoryError: If ``log_dir`` exists but is not a directory.

    Returns:
        int: Number of files processed (also when ``dry_run`` is ``True``).

    """
    if keep_days < 0:
        raise ValueError("keep_days must be non-negative")

    if log_dir is None:
        log_dir = Path(__file__).resolve().parent.parent / "loglar"
    else:
        log_dir = Path(log_dir)
    if not log_dir.exists():  # short-circuit when directory is absent
        return 0
    if not log_dir.is_dir():
        raise NotADirectoryError(str(log_dir))
    if patterns is None:
        patterns = ("*.log*",)
    elif isinstance(patterns, str):
        patterns = (patterns,)
    else:
        patterns = tuple(patterns)

    cutoff_ts = (datetime.now() - timedelta(days=keep_days)).timestamp()
    count = 0

    def remove_file(path: Path) -> None:
        """Delete ``path`` unless ``dry_run`` is enabled."""
        if dry_run:
            msg = f"[DRY-RUN] Would delete {path}"
            if logger:
                logger.info(msg)
            else:
                print(msg)
        else:
            path.unlink(missing_ok=True)
            if logger:
                logger.debug("Deleted %s", path)

    def is_expired(p: Path) -> bool:
        """Return ``True`` when ``p`` is older than the cutoff timestamp."""
        try:
            return p.stat().st_mtime < cutoff_ts
        except FileNotFoundError:  # pragma: no cover - race condition
            return False

    seen: set[Path] = set()
    for pat in patterns:
        for log_file in log_dir.glob(pat):
            if log_file in seen:
                continue
            seen.add(log_file)
            if is_expired(log_file):
                remove_file(log_file)
                count += 1
                lock = log_file.with_suffix(".lock")
                if lock.exists():
                    remove_file(lock)
                    count += 1

    for lock_file in log_dir.glob("*.lock"):
        if not lock_file.with_suffix(".log").exists() and is_expired(lock_file):
            remove_file(lock_file)
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
