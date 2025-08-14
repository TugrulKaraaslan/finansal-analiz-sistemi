from __future__ import annotations

import logging
import os
import sys
import time
from datetime import datetime
from logging.handlers import RotatingFileHandler

_DEF_LEVEL = os.getenv("BIST_LOG_LEVEL", "INFO").upper()


class Timer:
    def __init__(self, name: str):
        self.name = name
        self.t0 = None

    def __enter__(self):
        self.t0 = time.perf_counter()
        logging.info(f"▶️  start: {self.name}")
        return self

    def __exit__(self, exc_type, exc, tb):
        dt = (time.perf_counter() - self.t0) * 1000
        if exc:
            logging.exception(f"❌ fail: {self.name} in {dt:.1f} ms")
        else:
            logging.info(f"✅ done: {self.name} in {dt:.1f} ms")


_DEF_FMT = "%(asctime)s | %(levelname)-7s | %(name)s | %(message)s"

_def_handler = None


def setup_logger(
    run_id: str | None = None, level: str = _DEF_LEVEL, log_dir: str = "logs"
) -> str:
    global _def_handler
    os.makedirs(log_dir, exist_ok=True)
    stamp = run_id or datetime.now().strftime("%Y%m%d_%H%M%S")
    logfile = os.path.join(log_dir, f"colab_run_{stamp}.log")

    root = logging.getLogger()
    root.setLevel(getattr(logging, level, logging.INFO))

    # console
    if not any(isinstance(h, logging.StreamHandler) for h in root.handlers):
        ch = logging.StreamHandler(sys.stdout)
        ch.setFormatter(logging.Formatter(_DEF_FMT))
        root.addHandler(ch)

    # file (rotating)
    if _def_handler:
        root.removeHandler(_def_handler)
    _def_handler = RotatingFileHandler(logfile, maxBytes=5_000_000, backupCount=2)
    _def_handler.setFormatter(logging.Formatter(_DEF_FMT))
    root.addHandler(_def_handler)

    logging.info(f"Log file: {logfile}")
    return logfile
