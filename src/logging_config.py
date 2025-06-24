import logging
from logging.handlers import RotatingFileHandler
import os

# ——— Config ———
LOG_DIR = os.getenv("LOG_DIR", "loglar")
os.makedirs(LOG_DIR, exist_ok=True)

# Boyut bazlı rotasyon — 2 MB, 3 yedek
handler = RotatingFileHandler(
    f"{LOG_DIR}/run.log",
    maxBytes=2_000_000,   # 2 MB
    backupCount=3,        # run.log, .1, .2, .3
    encoding="utf-8",
)
handler.setFormatter(
    logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s")
)

root = logging.getLogger()
root.setLevel(logging.INFO)
root.addHandler(handler)
