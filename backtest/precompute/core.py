import pandas as pd
import pandas_ta as ta
import re
from typing import Set, Dict, Any

from .errors import PrecomputeError

# regex: rsi_14, ema_50, sma_20, macd_12_26_9, bbh_20_2
_SIMPLE_RE = re.compile(r"^(?P<name>[a-z]+)_([0-9_]+)$")

class Precomputer:
    def __init__(self):
        self.cache: Set[str] = set()

    def precompute(self, df: pd.DataFrame, indicators: Set[str]) -> pd.DataFrame:
        out = df.copy()
        for ind in sorted(indicators):
            if ind in self.cache:
                continue
            try:
                out = self._compute_one(out, ind)
                self.cache.add(ind)
            except Exception as e:
                raise PrecomputeError(f"Gösterge hesaplanamadı: {ind} | {e}", code="PC001")
        return out

    def _compute_one(self, df: pd.DataFrame, ind: str) -> pd.DataFrame:
        if ind.startswith("rsi_"):
            length = int(ind.split("_")[1])
            df[ind] = ta.rsi(df["close"], length=length)
        elif ind.startswith("ema_"):
            length = int(ind.split("_")[1])
            df[ind] = ta.ema(df["close"], length=length)
        elif ind.startswith("sma_"):
            length = int(ind.split("_")[1])
            df[ind] = ta.sma(df["close"], length=length)
        elif ind.startswith("wma_"):
            length = int(ind.split("_")[1])
            df[ind] = ta.wma(df["close"], length=length)
        elif ind.startswith("adx_"):
            length = int(ind.split("_")[1])
            df[ind] = ta.adx(df["high"], df["low"], df["close"], length=length)["ADX_"+str(length)]
        elif ind.startswith("dmp_"):
            length = int(ind.split("_")[1])
            df[ind] = ta.adx(df["high"], df["low"], df["close"], length=length)["DMP_"+str(length)]
        elif ind.startswith("dmn_"):
            length = int(ind.split("_")[1])
            df[ind] = ta.adx(df["high"], df["low"], df["close"], length=length)["DMN_"+str(length)]
        elif ind.startswith("macd_"):
            parts = ind.split("_")[1:]
            if len(parts) != 3:
                raise PrecomputeError(f"macd parametre hatası: {ind}", code="PC002")
            fast, slow, sig = map(int, parts)
            macd = ta.macd(df["close"], fast=fast, slow=slow, signal=sig)
            df[f"macd_{fast}_{slow}_{sig}"] = macd[f"MACD_{fast}_{slow}_{sig}"]
            df[f"macd_signal_{fast}_{slow}_{sig}"] = macd[f"MACDs_{fast}_{slow}_{sig}"]
            df[f"macd_hist_{fast}_{slow}_{sig}"] = macd[f"MACDh_{fast}_{slow}_{sig}"]
        elif ind.startswith("bbh_") or ind.startswith("bbm_") or ind.startswith("bbl_"):
            parts = ind.split("_")[1:]
            if len(parts) != 2:
                raise PrecomputeError(f"bollinger parametre hatası: {ind}", code="PC002")
            length, mult = map(int, parts)
            bb = ta.bbands(df["close"], length=length, std=mult)
            df[f"bbl_{length}_{mult}"] = bb[f"BBL_{length}_{mult}.0"]
            df[f"bbm_{length}_{mult}"] = bb[f"BBM_{length}_{mult}.0"]
            df[f"bbh_{length}_{mult}"] = bb[f"BBU_{length}_{mult}.0"]
        else:
            raise PrecomputeError(f"Desteklenmeyen gösterge: {ind}", code="PC001")
        return df
