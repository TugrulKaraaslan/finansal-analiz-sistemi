import sys
from pathlib import Path

import numpy as np
import pandas as pd

# Allow running directly via `python tools/make_excel_fixtures.py`
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backtest.paths import EXCEL_DIR

EXCEL_DIR.mkdir(parents=True, exist_ok=True)

# Tarih aralığı: testlerin kullandığı aralıkları içersin
dates = pd.date_range("2025-03-01", periods=12, freq="B")

# AAA örnek datası (minimum gerekli kolonlar)
df = pd.DataFrame(
    {
        "date": dates,
        "open": np.linspace(100, 110, len(dates)),
        "high": np.linspace(101, 112, len(dates)),
        "low": np.linspace(99, 108, len(dates)),
        "close": np.linspace(100, 109, len(dates)),
        "volume": np.linspace(1e5, 1.2e5, len(dates)).astype(int),
        # Ichimoku/MACD/Bollinger için kanonik kolonlar
        "ichimoku_conversionline": np.linspace(100, 105, len(dates)),
        "ichimoku_baseline": np.linspace(99, 104, len(dates)),
        "macd_line": np.sin(np.linspace(0, 2 * np.pi, len(dates))) / 10,
        "macd_signal": np.zeros(len(dates)),
        "bbm_20_2": np.linspace(100, 104, len(dates)),
        "bbu_20_2": np.linspace(101, 106, len(dates)),
        "bbl_20_2": np.linspace(99, 102, len(dates)),
    }
)

# AAA.xlsx (sheet adı AAA)
df.to_excel(EXCEL_DIR / "AAA.xlsx", sheet_name="AAA", index=False)

# BIST benchmark (opsiyonel ama eksik uyarısı yaşanmaması için ekle)
bist = pd.DataFrame({"date": dates, "close": np.linspace(3000, 3050, len(dates))})
bist.to_excel(EXCEL_DIR / "BIST.xlsx", sheet_name="BIST", index=False)

print(f"Excel fixtures written under: {EXCEL_DIR}")
