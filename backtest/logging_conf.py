from __future__ import annotations
import json
import logging
import os
import sys
import uuid
from pathlib import Path
from datetime import datetime
from contextvars import ContextVar

run_id_var: ContextVar[str] = ContextVar("run_id", default=None)
fold_id_var: ContextVar[str] = ContextVar("fold_id", default=None)


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:  # pragma: no cover - simple
        base = {
            "ts": datetime.utcfromtimestamp(record.created).strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
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
_LOG_DIR = Path(os.getenv("LOG_DIR", "artifacts/logs"))
_LOG_DIR.mkdir(parents=True, exist_ok=True)
_LOG_FILE = _LOG_DIR / ("app-" + datetime.utcnow().strftime("%Y%m%d-%H%M%S") + ".jsonl")

_initialized = False


def ensure_run_id() -> str:
    rid = os.getenv("BACKTEST_RUN_ID") or str(uuid.uuid4())
    run_id_var.set(rid)
    return rid


def set_fold_id(fid: str | None) -> None:
    fold_id_var.set(fid)


def get_logger(name: str = "app") -> logging.Logger:
    global _initialized
    if not _initialized:
        level = getattr(logging, _DEF_LEVEL, logging.INFO)
        logging.captureWarnings(True)
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
        fh = logging.FileHandler(_LOG_FILE, encoding="utf-8")
        fh.setFormatter(JsonFormatter())
        root.addHandler(fh)
        _initialized = True
        ensure_run_id()
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
