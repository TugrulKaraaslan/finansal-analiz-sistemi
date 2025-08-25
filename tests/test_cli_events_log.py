from backtest import cli


def test_cli_creates_events(tmp_path, monkeypatch):
    log_root = tmp_path / "logs"
    art_root = tmp_path / "art"
    monkeypatch.setenv("LOG_DIR", str(log_root))
    monkeypatch.setenv("ARTIFACTS_DIR", str(art_root))
    cli.main(["guardrails", "--out-dir", str(tmp_path / "out")])
    run_dirs = [p for p in log_root.iterdir() if p.is_dir()]
    assert run_dirs, "no run directory created"
    events = run_dirs[0] / "events.jsonl"
    assert events.exists()
    assert events.read_text().strip()
