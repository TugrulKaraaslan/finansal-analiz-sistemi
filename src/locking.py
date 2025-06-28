import tempfile
from uuid import uuid4
from pathlib import Path
import portalocker

# Unique lock file in temp directory
LOCK_PATH = Path(tempfile.gettempdir()) / f"{uuid4()}.lock"


def acquire_lock():
    """Return a lock object with 10s timeout."""
    return portalocker.Lock(LOCK_PATH, timeout=10)
