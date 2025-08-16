"""Logging utilities for backtest package.

This module centralises logging configuration and timing helpers.  It
implements a simple structured logging scheme where each execution
creates a dedicated run directory under ``loglar/``.

Example::

    >>> from backtest.logging_utils import setup_logger, Timer
    >>> logfile = setup_logger(run_id="example")
    >>> with Timer("stage") as t:
    ...     t.update(rows=10)

The above snippet will create ``loglar/run_example`` with files such as
``summary.txt`` and ``stages.jsonl``.
"""

from __future__ import annotations

import json
import logging
import os
import shutil
import sys
import time
from datetime import datetime, timedelta, timezone
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Any, Callable

__all__ = ["Timer", "setup_logger", "purge_old_logs"]


_DEF_LEVEL = os.getenv("BIST_LOG_LEVEL", "INFO").upper()
_DEF_FMT = "%(asctime)s | %(levelname)-7s | %(name)s | %(message)s"

_def_handler: RotatingFileHandler | None = None
_RUN_DIR: Path | None = None


class Timer:
    """Context manager & decorator to measure execution time.

    Parameters
    ----------
    stage:
        Name of the stage being timed.
    extra:
        Optional initial metrics that will be written to ``stages.jsonl``.
    """

    def __init__(self, stage: str, *, extra: dict[str, Any] | None = None):
        self.stage = stage
        self.extra = extra or {}
        self.t0: float | None = None
        self.start: datetime | None = None

    # ------------------------------------------------------------------
    # Context manager API
    # ------------------------------------------------------------------
    def __enter__(self) -> "Timer":  # pragma: no cover - trivial
        self.t0 = time.perf_counter()
        self.start = datetime.now(timezone.utc)
        logging.info("▶️  start: %s", self.stage)
        return self

    def __exit__(self, exc_type, exc, tb) -> bool:
        assert self.t0 is not None and self.start is not None
        end = datetime.now(timezone.utc)
        dt_ms = int((time.perf_counter() - self.t0) * 1000)

        record = {
            "ts": end.isoformat(),
            "stage": self.stage,
            "elapsed_ms": dt_ms,
            "start": self.start.isoformat(),
            "end": end.isoformat(),
            **self.extra,
        }

        stages_path = _RUN_DIR / "stages.jsonl" if _RUN_DIR else None

        if exc_type:
            logging.exception("❌ fail: %s in %d ms", self.stage, dt_ms)
            record["level"] = "ERROR"
            if _RUN_DIR:
                err_file = _RUN_DIR / f"{self.stage}.err"
                with err_file.open("w", encoding="utf-8") as fh:
                    import traceback

                    traceback.print_exception(exc_type, exc, tb, file=fh)
        else:
            logging.info("✅ done: %s in %d ms", self.stage, dt_ms)
            record["level"] = "INFO"

        if stages_path:
            with stages_path.open("a", encoding="utf-8") as fh:
                fh.write(json.dumps(record, ensure_ascii=False) + "\n")

        return False  # do not suppress exceptions

    # ------------------------------------------------------------------
    # Helper methods
    # ------------------------------------------------------------------
    def update(self, **metrics: Any) -> None:
        """Add metrics to be stored when the context exits."""

        self.extra.update(metrics)

    # ------------------------------------------------------------------
    # Decorator support
    # ------------------------------------------------------------------
    def __call__(self, func: Callable[..., Any]) -> Callable[..., Any]:
        """Allow ``Timer"`` to be used as a decorator."""

        def wrapper(*args: Any, **kwargs: Any) -> Any:
            with Timer(self.stage, extra=self.extra.copy()):
                return func(*args, **kwargs)

        return wrapper


def setup_logger(
    run_id: str | None = None,
    level: str = _DEF_LEVEL,
    log_dir: str = "loglar",
) -> str:
    """Initialise root logger and return main log file path.

    A new run directory ``run_<timestamp>`` is created under ``log_dir``.
    ``summary.txt`` within this directory is used as the main log file.
    ``setup_logger`` also sets a module level ``_RUN_DIR`` used by
    :class:`Timer`.
    """

    global _def_handler, _RUN_DIR

    base = Path(log_dir)
    base.mkdir(parents=True, exist_ok=True)

    stamp = run_id or datetime.now().strftime("%Y%m%d-%H%M%S")
    run_dir = base / f"run_{stamp}"
    run_dir.mkdir(parents=True, exist_ok=True)

    logfile = run_dir / "summary.txt"

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

    logging.info("Log dir: %s", run_dir)

    _RUN_DIR = run_dir
    return str(logfile)


def purge_old_logs(days: int = 7, log_dir: str = "loglar") -> list[str]:
    """Remove run directories older than ``days`` and return removed paths."""

    base = Path(log_dir)
    if not base.exists():
        return []

    cutoff = datetime.now() - timedelta(days=days)
    removed: list[str] = []
    for d in base.glob("run_*"):
        try:
            if d.is_dir() and datetime.fromtimestamp(d.stat().st_mtime) < cutoff:
                shutil.rmtree(d, ignore_errors=True)
                removed.append(str(d))
        except Exception:  # pragma: no cover - best effort
            pass
    return removed
