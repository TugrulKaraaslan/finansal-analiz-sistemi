from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path
import logging

_LOG = logging.getLogger(__name__)


def purge_old_logs(
    dir_path: str | Path = "loglar",
    days: int = 7,
    *,
    dry_run: bool = False,
) -> int:
    """Belirtilen klasördeki *.log dosyalarını yaş filtresiyle sil.

    Args:
        dir_path: Log dosyalarının bulunduğu klasör.
        days: Kaç günden eski dosyalar silinsin.
        dry_run: *True* ise sadece hangi dosyaların silineceğini INFO ile yazar.

    Returns
    -------
    int
        Silinen dosya sayısı (dry-run modunda her zaman *0*).
    """

    cutoff = datetime.now() - timedelta(days=days)
    deleted = 0
    for fp in Path(dir_path).glob("*.log"):
        if datetime.fromtimestamp(fp.stat().st_mtime) < cutoff:
            _LOG.info("%s %s", "Would delete" if dry_run else "Deleted", fp)
            if not dry_run:
                fp.unlink(missing_ok=True)
                deleted += 1
    return deleted
