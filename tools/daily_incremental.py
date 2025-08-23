from __future__ import annotations
from zoneinfo import ZoneInfo
from datetime import datetime, timedelta
from pathlib import Path
import os, subprocess, sys, json

IST = ZoneInfo("Europe/Istanbul")

# Parametreler (env ile override edilebilir)
DAYS_BACK = int(os.getenv("DAYS_BACK", "1"))   # kaç gün geriye bakılacak (varsayılan 1 = dün)
CONFIG = os.getenv("CONFIG", "config/colab_config.yaml")
WEBHOOK = os.getenv("WEBHOOK_URL")  # opsiyonel
MSG_PREFIX = os.getenv("MESSAGE_PREFIX", "[daily]")

# Hedef tarih (İstanbul takvimine göre dün)
now_tr = datetime.now(tz=IST)
target = (now_tr - timedelta(days=DAYS_BACK)).date().isoformat()

# Çıktı klasörü (tarihe göre)
OUTDIR = Path(f"artifacts/daily/{target}")
OUTDIR.mkdir(parents=True, exist_ok=True)

# Komut: sadece bir gün tarıyoruz
CMD = [sys.executable, "-m", "backtest.cli", "scan-range",
       "--config", CONFIG,
       "--start", target, "--end", target]

res = subprocess.run(CMD, capture_output=True, text=True)
rec = {
    "ts": now_tr.isoformat(),
    "target_date": target,
    "cmd": " ".join(CMD),
    "returncode": res.returncode,
    "stdout_tail": res.stdout[-400:],
    "stderr_tail": res.stderr[-400:],
}
(OUTDIR/"run.json").write_text(json.dumps(rec, indent=2, ensure_ascii=False), encoding="utf-8")

# Basit bildirim (opsiyonel webhook; generic JSON POST formatı)
if WEBHOOK:
    try:
        import urllib.request, json as _json
        payload = {
            "text": f"{MSG_PREFIX} {target} return={res.returncode}",
            "details": rec,
        }
        req = urllib.request.Request(WEBHOOK, data=_json.dumps(payload).encode("utf-8"), headers={"Content-Type":"application/json"})
        urllib.request.urlopen(req, timeout=10).read()
    except Exception as _:
        pass

print(json.dumps(rec, indent=2, ensure_ascii=False))
sys.exit(res.returncode)
