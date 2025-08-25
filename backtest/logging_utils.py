"""Logging utilities for the backtest package.

This module centralises logging configuration and provides a small
``Timer`` helper used throughout the project.  Each execution is assigned
to a *run directory* under ``loglar/`` where structured log events are
written as ``events.jsonl``.
"""

from __future__ import annotations

import json
import logging
import os
import shutil
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Callable

from loguru import logger

__all__ = ["Timer", "setup_logger", "purge_old_logs"]


_DEF_LEVEL = os.getenv("BIST_LOG_LEVEL", "INFO").upper()
_DEF_FMT = "%(asctime)s | %(levelname)-7s | %(name)s | %(message)s"

_RUN_DIR: Path | None = None
_RUN_ID: str | None = None
_EVENT_KEY = "_event"

_METRIC_KEYS = [
    "rows",
    "symbols",
    "signals",
    "trades",
    "rows_written",
    "duration_ms",
]


class Timer:
    """Context manager and decorator measuring execution time."""

    def __init__(self, stage: str, *, extra: dict[str, Any] | None = None):
        self.stage = stage
        self.t0: float | None = None
        self.start: datetime | None = None
        self.day: str | None = None
        self.diag: str | None = None
        self.metrics: dict[str, Any] = {k: 0 for k in _METRIC_KEYS}
        self.extra: dict[str, Any] = {}
        if extra:
            self.update(**extra)

    # ------------------------------------------------------------------
    # Context manager API
    # ------------------------------------------------------------------
    def __enter__(self) -> "Timer":  # pragma: no cover - trivial
        self.t0 = time.perf_counter()
        self.start = datetime.now(timezone.utc)
        logger.info("▶️  start: {}", self.stage)
        return self

    def __exit__(self, exc_type, exc, tb) -> bool:
        assert self.t0 is not None
        end = datetime.now(timezone.utc)
        dt_ms = int((time.perf_counter() - self.t0) * 1000)
        self.metrics["duration_ms"] = dt_ms

        level = "ERROR" if exc_type else "INFO"
        record = {
            "ts": end.isoformat(),
            "level": level,
            "stage": self.stage,
            "run_id": _RUN_ID,
            "day": self.day,
            "metrics": {k: self.metrics.get(k, 0) for k in _METRIC_KEYS},
            "diag": self.diag or "None",
        }

        if exc_type:
            logger.exception("❌ fail: {} in {} ms", self.stage, dt_ms)
            if _RUN_DIR:
                err_file = _RUN_DIR / f"{self.stage}.err"
                with err_file.open("w", encoding="utf-8") as fh:
                    import traceback

                    traceback.print_exception(exc_type, exc, tb, file=fh)
        else:
            logger.info("✅ done: {} in {} ms", self.stage, dt_ms)

        if _RUN_DIR:
            logger.bind(**{_EVENT_KEY: True}).log(
                level, json.dumps(record, ensure_ascii=False)
            )
            stages_path = _RUN_DIR / "stages.jsonl"
            legacy = {
                "ts": end.isoformat(),
                "stage": self.stage,
                "elapsed_ms": dt_ms,
                "start": self.start.isoformat() if self.start else None,
                "end": end.isoformat(),
                **self.metrics,
                **self.extra,
                "level": level,
            }
            with stages_path.open("a", encoding="utf-8") as fh:
                fh.write(json.dumps(legacy, ensure_ascii=False) + "\n")

        self.elapsed_ms = dt_ms
        return False  # do not suppress exceptions

    # ------------------------------------------------------------------
    # Helper methods
    # ------------------------------------------------------------------
    def update(self, **metrics: Any) -> None:
        for k, v in metrics.items():
            if k == "day":
                self.day = v
            elif k == "diag":
                self.diag = v
            elif k in _METRIC_KEYS:
                self.metrics[k] = v
            else:
                self.extra[k] = v

    # ------------------------------------------------------------------
    # Decorator support
    # ------------------------------------------------------------------
    def __call__(self, func: Callable[..., Any]) -> Callable[..., Any]:
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            with Timer(
                self.stage,
                extra={
                    "day": self.day,
                    "diag": self.diag,
                    **{k: v for k, v in self.metrics.items() if v},
                },
            ):
                return func(*args, **kwargs)

        return wrapper


def setup_logger(
    run_id: str | None = None,
    level: str = _DEF_LEVEL,
    log_dir: str = "loglar",
    json_console: bool = False,
) -> str:
    """Initialise loggers and return the ``events.jsonl`` path."""

    global _RUN_DIR, _RUN_ID

    base = Path(log_dir)
    base.mkdir(parents=True, exist_ok=True)

    stamp = run_id or datetime.now().strftime("%Y%m%d-%H%M%S")
    run_dir = base / f"run_{stamp}"
    run_dir.mkdir(parents=True, exist_ok=True)

    _RUN_DIR = run_dir
    _RUN_ID = stamp

    events_path = run_dir / "events.jsonl"

    class InterceptHandler(logging.Handler):
        def emit(self, record: logging.LogRecord) -> None:  # pragma: no cover - thin
            try:
                lvl = logger.level(record.levelname).name
            except ValueError:
                lvl = record.levelno
            logger.bind().opt(depth=6, exception=record.exc_info).log(
                lvl, record.getMessage()
            )

    logging.basicConfig(handlers=[InterceptHandler()], level=0)

    logger.remove()
    logger.add(
        sys.stdout,
        level=level,
        serialize=json_console,
        format=None if json_console else _DEF_FMT,
    )
    logger.add(
        events_path,
        level="DEBUG",
        rotation="10 MB",
        format="{message}",
        filter=lambda r: r["extra"].get(_EVENT_KEY, False),
    )
    # ensure file exists with a start marker
    start_event = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "level": "INFO",
        "stage": "summary",
        "run_id": _RUN_ID,
        "day": None,
        "metrics": {k: 0 for k in _METRIC_KEYS},
        "diag": "None",
    }
    logger.bind(**{_EVENT_KEY: True}).info(json.dumps(start_event, ensure_ascii=False))

    return str(events_path)


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

