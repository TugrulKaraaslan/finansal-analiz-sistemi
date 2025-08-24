import subprocess
import sys
from pathlib import Path

from pyinstrument import Profiler


def main():
    Path("artifacts/profiles").mkdir(parents=True, exist_ok=True)
    profiler = Profiler()
    profiler.start()
    # Örnek: scan-range kısa aralık
    subprocess.run(
        [
            sys.executable,
            "-m",
            "backtest.cli",
            "scan-range",
            "--config",
            "config/colab_config.yaml",
            "--start",
            "2025-03-07",
            "--end",
            "2025-03-09",
        ],
        check=False,
    )
    profiler.stop()
    html = profiler.output_html()
    out = Path("artifacts/profiles/pyinstrument_scan.html")
    out.write_text(html, encoding="utf-8")
    print(f"profile written: {out}")


if __name__ == "__main__":
    main()
