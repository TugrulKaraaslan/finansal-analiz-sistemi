from __future__ import annotations

import json
import os
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Iterable

import pandas as pd

from backtest.paths import DATA_DIR, PROJECT_ROOT
from .schema import CANON_COLS, normalize


class DataDownloader:
    """Core downloader managing manifest, locks and Parquet outputs."""

    def __init__(
        self,
        provider,
        data_dir: str | Path = DATA_DIR / "parquet",
        manifest_path: str | Path = PROJECT_ROOT / "artifacts/data/manifest.json",
    ) -> None:
        self.provider = provider
        self.data_dir = Path(data_dir)
        self.manifest_path = Path(manifest_path)
        self.lock_path = self.manifest_path.parent / ".lock"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.manifest_path.parent.mkdir(parents=True, exist_ok=True)
        self._manifest: dict = self._load_manifest()

    # ---- manifest & lock helpers -------------------------------------------------
    def _load_manifest(self) -> dict:
        if self.manifest_path.exists():
            with open(self.manifest_path) as f:
                return json.load(f)
        return {}

    def _save_manifest(self) -> None:
        with open(self.manifest_path, "w") as f:
            json.dump(self._manifest, f, indent=2, sort_keys=True)

    @contextmanager
    def _lock(self):
        fd = os.open(self.lock_path, os.O_CREAT | os.O_EXCL | os.O_RDWR)
        try:
            yield
        finally:
            os.close(fd)
            os.remove(self.lock_path)

    # ---- internal operations -----------------------------------------------------
    def _write_symbol(self, symbol: str, df: pd.DataFrame) -> None:
        sym_dir = self.data_dir / f"symbol={symbol}"
        sym_dir.mkdir(parents=True, exist_ok=True)
        df = df.sort_values("date")
        for yyyymm, g in df.groupby(df["date"].dt.strftime("%Y%m")):
            part = sym_dir / f"part-{yyyymm}.parquet"
            if part.exists():
                existing = pd.read_parquet(part)
                g = (
                    pd.concat([existing, g])
                    .drop_duplicates("date")
                    .sort_values("date")
                    .reset_index(drop=True)
                )
            g.to_parquet(part, index=False)

    # ---- public API --------------------------------------------------------------
    def fetch_range(self, symbols: Iterable[str], start, end) -> None:
        start = pd.to_datetime(start).date()
        end = pd.to_datetime(end).date()
        for symbol in symbols:
            df = self.provider.fetch(symbol, start, end)
            if df.empty:
                continue
            df = normalize(df)
            with self._lock():
                self._write_symbol(symbol, df)
                self._manifest[symbol] = {
                    "last_fetch_ts": datetime.utcnow().isoformat(),
                    "last_date": df["date"].max().date().isoformat(),
                    "source": getattr(self.provider, "name", "provider"),
                    "ttl_hours": getattr(self.provider, "ttl_hours", 0),
                }
                self._save_manifest()

    def fetch_latest(self, symbols: Iterable[str], ttl_hours: int) -> None:
        now = datetime.utcnow()
        for symbol in symbols:
            info = self._manifest.get(symbol)
            if info:
                last_ts = pd.to_datetime(info["last_fetch_ts"])
                if now - last_ts < pd.Timedelta(hours=ttl_hours):
                    continue
                start = pd.to_datetime(info["last_date"]).date() + pd.Timedelta(days=1)
            else:
                start = now.date()
            end = now.date()
            if start > end:
                continue
            df = self.provider.fetch(symbol, start, end)
            if df.empty:
                continue
            df = normalize(df)
            with self._lock():
                self._write_symbol(symbol, df)
                self._manifest[symbol] = {
                    "last_fetch_ts": now.isoformat(),
                    "last_date": df["date"].max().date().isoformat(),
                    "source": getattr(self.provider, "name", "provider"),
                    "ttl_hours": ttl_hours,
                }
                self._save_manifest()

    def refresh_cache(self, ttl_hours: int = 0) -> None:
        self.fetch_latest(self._manifest.keys(), ttl_hours)

    def vacuum_cache(self, older_than_days: int = 365) -> None:
        cutoff = datetime.utcnow() - pd.Timedelta(days=older_than_days)
        for part in self.data_dir.glob("**/*.parquet"):
            if datetime.utcfromtimestamp(part.stat().st_mtime) < cutoff:
                part.unlink()

    def integrity_check(self, symbols: Iterable[str]) -> dict:
        report = {}
        for symbol in symbols:
            sym_dir = self.data_dir / f"symbol={symbol}"
            if not sym_dir.exists():
                report[symbol] = {"missing": True}
                continue
            dfs = [pd.read_parquet(p) for p in sorted(sym_dir.glob("part-*.parquet"))]
            if not dfs:
                report[symbol] = {"missing": True}
                continue
            df = pd.concat(dfs).sort_values("date").reset_index(drop=True)
            issues: list[str] = []
            if df["date"].duplicated().any():
                issues.append("duplicate_dates")
            if not df["date"].is_monotonic_increasing:
                issues.append("not_sorted")
            if set(CANON_COLS) - set(df.columns):
                issues.append("missing_cols")
            if df.isna().any().any():
                issues.append("nan_values")
            if (df["date"].dt.weekday >= 5).any():
                issues.append("weekend")
            expected = pd.date_range(df["date"].min(), df["date"].max(), freq="B")
            missing = expected.difference(df["date"])
            if not missing.empty:
                issues.append("gaps")
            report[symbol] = {"issues": issues}
        out = self.manifest_path.parent / "integrity_report.json"
        with open(out, "w") as f:
            json.dump(report, f, indent=2, sort_keys=True)
        return report
