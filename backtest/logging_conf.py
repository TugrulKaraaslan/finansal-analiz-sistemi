from __future__ import annotations

import json
import logging
import os
import sys
import uuid
from contextvars import ContextVar
from datetime import datetime, UTC
from pathlib import Path

run_id_var: ContextVar[str] = ContextVar("run_id", default=None)
fold_id_var: ContextVar[str] = ContextVar("fold_id", default=None)


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:  # pragma: no cover - simple
        ts = datetime.fromtimestamp(record.created, UTC).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        base = {
            "ts": ts,
            "level": record.levelname,
            "logger": record.name,
            "msg": record.getMessage(),
        }
        extra = getattr(record, "extra_fields", {})
        if not isinstance(extra, dict):
            extra = {}
        base.update(extra)
        rid = run_id_var.get()
        fid = fold_id_var.get()
        if rid:
            base.setdefault("run_id", rid)
        if fid:
            base.setdefault("fold_id", fid)
        if record.exc_info:
            base["exc_type"] = record.exc_info[0].__name__
        return json.dumps(base, ensure_ascii=False)


_DEF_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
_DEF_FMT = os.getenv("LOG_FORMAT", "json").lower()  # json | plain
_initialized = False
_LOG_FILE: Path | None = None


def ensure_run_id() -> str:
    rid = os.getenv("BACKTEST_RUN_ID") or str(uuid.uuid4())
    run_id_var.set(rid)
    return rid


def set_fold_id(fid: str | None) -> None:
    fold_id_var.set(fid)


def setup_logger(log_dir: Path | str = "loglar", *, capture_warnings: bool = False) -> logging.Logger:
    """Configure root logger and return it.

    ``capture_warnings`` controls :func:`logging.captureWarnings` and the
    ``py.warnings`` logger is isolated to avoid recursive logging.
    """

    global _initialized, _LOG_FILE

    if not _initialized:
        level = getattr(logging, _DEF_LEVEL, logging.INFO)
        root = logging.getLogger()
        root.setLevel(level)

        sh = logging.StreamHandler(stream=sys.stdout)
        if _DEF_FMT == "json":
            sh.setFormatter(JsonFormatter())
        else:
            sh.setFormatter(
                logging.Formatter("%(asctime)s %(levelname)s [%(name)s] %(message)s")
            )
        root.addHandler(sh)

        base = Path(log_dir)
        base.mkdir(parents=True, exist_ok=True)
        fname = "app-" + datetime.now(UTC).strftime("%Y%m%d-%H%M%S") + ".jsonl"
        _LOG_FILE = base / fname
        fh = logging.FileHandler(_LOG_FILE, encoding="utf-8")
        fh.setFormatter(JsonFormatter())
        root.addHandler(fh)

        ensure_run_id()
        _initialized = True

    logging.captureWarnings(capture_warnings)
    wlog = logging.getLogger("py.warnings")
    wlog.handlers.clear()
    wlog.addHandler(logging.StreamHandler(sys.stderr))
    wlog.propagate = False

    return logging.getLogger()


def get_logger(name: str = "app") -> logging.Logger:
    if not _initialized:
        setup_logger()
    return logging.getLogger(name)


def log_with(logger: logging.Logger, level: str, msg: str, **fields) -> None:
    rec = logger.makeRecord(
        logger.name,
        getattr(logging, level.upper(), logging.INFO),
        fn="",
        lno=0,
        msg=msg,
        args=(),
        exc_info=None,
    )
    setattr(rec, "extra_fields", fields)
    logger.handle(rec)
