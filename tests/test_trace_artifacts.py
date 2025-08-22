import os
import json
from pathlib import Path
import pandas as pd
import numpy as np
from backtest.trace import RunContext, ArtifactWriter, list_output_files, sha256_file


def test_run_context_and_artifacts(tmp_path: Path):
    logs = tmp_path / "logs"
    arts = tmp_path / "artifacts"
    rc = RunContext.create(logs, arts)
    rc.write_env_snapshot()
    rc.write_config_snapshot({"flags": {"a": 1}}, {"x": 1})
    assert (arts / rc.run_id / "env.json").exists()
    assert (arts / rc.run_id / "config.json").exists()
    assert (arts / rc.run_id / "inputs.json").exists()


def test_checksum_determinism(tmp_path: Path):
    out = tmp_path / "gunluk"
    out.mkdir(parents=True, exist_ok=True)
    f1 = out / "2024-01-01.csv"
    f1.write_text("date,symbol,filter_code\n2024-01-01,AAA,F1\n", encoding="utf-8")
    f2 = out / "2024-01-02.csv"
    f2.write_text("date,symbol,filter_code\n2024-01-02,BBB,F2\n", encoding="utf-8")

    files = list_output_files(out)
    writer = ArtifactWriter(tmp_path / "artifacts_run")
    p = writer.write_checksums(files)
    data = json.loads(p.read_text(encoding="utf-8"))
    # aynı dosyaların hash'i sabittir
    assert "2024-01-01.csv" in data and "2024-01-02.csv" in data
    # tek dosyanın manuel hash'i ile karşılaştır
    import hashlib
    h = hashlib.sha256(f1.read_bytes()).hexdigest()
    assert data["2024-01-01.csv"] == h
