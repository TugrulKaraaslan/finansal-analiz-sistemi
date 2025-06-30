import os
import tempfile
from pathlib import Path
from uuid import uuid4

import portalocker

# Benzersiz lock dosyası ismi (her oturumda farklı olur, çakışma önlenir)
LOCK_PATH = Path(tempfile.gettempdir()) / f"{uuid4()}.lock"

# Timeout: lock kilidi almak için maksimum bekleme süresi (saniye)
LOCK_TIMEOUT = int(os.getenv("LOCK_TIMEOUT", 10))  # ortamdan al, yoksa 10 sn


def acquire_lock():
    """
    Güvenli dosya kilidi döndürür.
    Paralel oturumlarda deadlock riskini azaltır.
    Timeout parametresi ile bekler, dosya kilitliyse belirli süre sonra vazgeçer.
    """
    return portalocker.Lock(LOCK_PATH, timeout=LOCK_TIMEOUT)
