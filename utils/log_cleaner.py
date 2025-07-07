from __future__ import annotations

import logging
from pathlib import Path

from .purge_old_logs import purge_old_logs as _impl

_LOG = logging.getLogger(__name__)


def purge_old_logs(
    dir_path: str | Path = "loglar",
    days: int = 7,
    *,
    dry_run: bool = False,
) -> int:
    """Belirtilen klasördeki ``*.log`` ve ``*.lock`` dosyalarını temizle.

    Returns the number of deleted files. When ``dry_run`` is *True*, no files
    are removed and ``0`` is returned.
    """

    _LOG.debug(
        "purge_old_logs called with dir_path=%s days=%d dry_run=%s",
        dir_path,
        days,
        dry_run,
    )
    count = _impl(log_dir=Path(dir_path), keep_days=days, dry_run=dry_run)
    return 0 if dry_run else count
