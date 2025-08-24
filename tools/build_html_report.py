from __future__ import annotations

import csv
import json
from datetime import datetime
from pathlib import Path

import pandas as pd
from jinja2 import Template

OUTDIR = Path("artifacts/report")
OUTDIR.mkdir(parents=True, exist_ok=True)


def _read_json(p: Path):
    try:
        return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None
    except Exception as e:
        return {"__error__": str(e)}


ctx = {
    "ts": datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC"),
    "wf_summary": _read_json(Path("artifacts/wf/summary.json")),
    "wf_results_path": (
        Path("artifacts/wf/results.jsonl").as_posix()
        if Path("artifacts/wf/results.jsonl").exists()
        else None
    ),
    "bench_scan": _read_json(Path("artifacts/bench/scan_bench.json")),
    "profile_path": (
        Path("artifacts/profiles/pyinstrument_scan.html").as_posix()
        if Path("artifacts/profiles/pyinstrument_scan.html").exists()
        else None
    ),
    "mem_top": _read_json(Path("artifacts/memory/top50.json")),
    "golden_checksums": _read_json(Path("tests/golden/checksums.json")),
    "quality_report": _read_json(Path("artifacts/quality/report.json")),
    "portfolio_daily": None,
    "portfolio_trades_head": None,
}

# Portföy günlük
p_daily = Path("artifacts/portfolio/daily_equity.csv")
if p_daily.exists():
    try:
        df = pd.read_csv(p_daily)
        ctx["portfolio_daily"] = {
            "rows": len(df),
            "start_equity": (
                float(df["equity"].iloc[0]) if "equity" in df.columns and len(df) > 0 else None
            ),
            "end_equity": (
                float(df["equity"].iloc[-1]) if "equity" in df.columns and len(df) > 0 else None
            ),
        }
    except Exception as e:
        ctx["portfolio_daily"] = {"__error__": str(e)}

# Portföy trades ilk 10 satır
p_trades = Path("artifacts/portfolio/trades.csv")
if p_trades.exists():
    try:
        import io

        head = "\n".join(p_trades.read_text(encoding="utf-8").splitlines()[:12])
        ctx["portfolio_trades_head"] = head
    except Exception as e:
        ctx["portfolio_trades_head"] = f"__error__: {e}"

TEMPLATE = Template(
    r"""
<!DOCTYPE html>
<html lang="tr">
<head>
  <meta charset="utf-8" />
  <title>Sonuç Dashboard’u</title>
  <style>
    body{font-family: system-ui, -apple-system, Segoe UI, Roboto, 'Helvetica Neue', Arial; margin:20px;}
    h1{margin:0 0 8px 0}
    .card{border:1px solid #e5e7eb; border-radius:12px; padding:16px; margin:12px 0;}
    .row{display:flex; gap:12px; flex-wrap:wrap}
    .col{flex:1 1 320px}
    code, pre{background:#f8fafc; padding:6px 8px; border-radius:8px; overflow:auto}
    .muted{color:#6b7280; font-size: 0.9em}
    table{border-collapse: collapse; width:100%}
    th, td{border:1px solid #e5e7eb; padding:6px 8px; text-align:left}
  </style>
</head>
<body>
  <h1>Sonuç Dashboard’u</h1>
  <div class="muted">Üretim: {{ ts }}</div>

  <div class="row">
    <div class="col card">
      <h3>Walk‑Forward</h3>
      {% if wf_summary %}
        <div>Fold sayısı: <b>{{ wf_summary.fold_count if wf_summary.get('fold_count') else wf_summary['fold_count'] }}</b></div>
        {% if wf_results_path %}<div class="muted">Detay: {{ wf_results_path }}</div>{% endif %}
      {% else %}
        <div class="muted">WF artefaktı bulunamadı.</div>
      {% endif %}
    </div>
    <div class="col card">
      <h3>Benchmark (CLI)</h3>
      {% if bench_scan %}
        <div>Çalıştırma: <code>{{ bench_scan.cmd }}</code></div>
        <div>Wall time: <b>{{ '%.2f' % bench_scan.wall_time_sec }} sn</b></div>
        <div>Return code: {{ bench_scan.returncode }}</div>
      {% else %}
        <div class="muted">Bench artefaktı yok.</div>
      {% endif %}
    </div>
  </div>

  <div class="row">
    <div class="col card">
      <h3>Profil (Pyinstrument)</h3>
      {% if profile_path %}
        <a href="../profiles/pyinstrument_scan.html">HTML profili (aç)</a>
      {% else %}
        <div class="muted">Profil artefaktı yok.</div>
      {% endif %}
    </div>
    <div class="col card">
      <h3>Bellek</h3>
      {% if mem_top %}
        <div>Top 5:</div>
        <pre>{{ (mem_top[:5] if mem_top is iterable else mem_top) | tojson(indent=2) }}</pre>
      {% else %}
        <div class="muted">Bellek artefaktı yok.</div>
      {% endif %}
    </div>
  </div>

  <div class="card">
    <h3>Portföy</h3>
    {% if portfolio_daily %}
      {% if portfolio_daily.__error__ %}
        <div class="muted">Hata: {{ portfolio_daily.__error__ }}</div>
      {% else %}
        <div>Satır: {{ portfolio_daily.rows }}, Başlangıç: {{ portfolio_daily.start_equity }}, Bitiş: {{ portfolio_daily.end_equity }}</div>
      {% endif %}
    {% else %}
      <div class="muted">Portföy artefaktı yok.</div>
    {% endif %}
    {% if portfolio_trades_head %}
      <h4>Trades (ilk satırlar)</h4>
      <pre>{{ portfolio_trades_head }}</pre>
    {% endif %}
  </div>

  <div class="row">
    <div class="col card">
      <h3>Golden</h3>
      {% if golden_checksums %}
        <div class="muted">tests/golden/checksums.json</div>
        <pre>{{ golden_checksums | tojson(indent=2) }}</pre>
      {% else %}
        <div class="muted">Golden bilgisi yok.</div>
      {% endif %}
    </div>
    <div class="col card">
      <h3>Veri Kalitesi</h3>
      {% if quality_report %}
        <pre>{{ quality_report | tojson(indent=2) }}</pre>
      {% else %}
        <div class="muted">Kalite raporu yok.</div>
      {% endif %}
    </div>
  </div>

</body>
</html>
"""
)

html = TEMPLATE.render(**ctx)
(OUTDIR / "index.html").write_text(html, encoding="utf-8")
print(f"wrote report → {OUTDIR/'index.html'}")
