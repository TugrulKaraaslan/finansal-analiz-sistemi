from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))
from backtest.eval.walk_forward import (  # noqa: E402
    WfParams,
    generate_folds,
    save_folds,
)
from backtest.logging_conf import get_logger, set_fold_id  # noqa: E402
from backtest.paths import DATA_DIR  # noqa: E402

log = get_logger("wf")

OUTDIR = Path("artifacts/wf")
OUTDIR.mkdir(parents=True, exist_ok=True)
ENV = dict(os.environ, DATA_DIR=str(DATA_DIR))

# Basit CLI parametreleri (env veya default)
start = os.getenv("WF_START", "2025-03-07")
end = os.getenv("WF_END", "2025-03-11")
train_days = int(os.getenv("WF_TRAIN_DAYS", "2"))
test_days = int(os.getenv("WF_TEST_DAYS", "1"))
step_days = int(os.getenv("WF_STEP_DAYS", "1"))
skip_scan = os.getenv("WF_SKIP_SCAN") == "1"

p = WfParams(start, end, train_days, test_days, step_days)
folds = generate_folds(p)
save_folds(folds, OUTDIR)

results_path = OUTDIR / "results.jsonl"
with results_path.open("w", encoding="utf-8") as w:
    for i, f in enumerate(folds):
        set_fold_id(str(i))
        log.info("wf fold", extra={"extra_fields": f})
        cmd = [
            sys.executable,
            "-m",
            "backtest.cli",
            "scan-range",
            "--config",
            "config_scan.yml",
            "--filters-csv",
            "tests/data/filters_valid.csv",
            "--no-preflight",
            "--start",
            f["train_start"],
            "--end",
            f["test_end"],
        ]
        # Not: İstersek ayrı ayrı train/test koşuluna ayrıştırırız;
        # burada smoke/örnek için tek komut yeterli
        res = (
            subprocess.CompletedProcess(cmd, 0, "", "")
            if skip_scan
            else subprocess.run(cmd, env=ENV, capture_output=True, text=True)
        )
        rec = {
            "fold": i,
            "train": [f["train_start"], f["train_end"]],
            "test": [f["test_start"], f["test_end"]],
            "cmd": " ".join(cmd),
            "returncode": res.returncode,
            "stderr_tail": res.stderr[-300:],
        }
        w.write(json.dumps(rec, ensure_ascii=False) + "\n")
        if res.returncode != 0:
            print(res.stderr)
            sys.exit(res.returncode)

# Özet
summary = {
    "fold_count": len(folds),
}
(Path(OUTDIR / "summary.json")).write_text(
    json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8"
)
print(json.dumps(summary, indent=2, ensure_ascii=False))
