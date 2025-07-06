"""Performans karşılaştırma betiği.

Bu script 1000 hisse için 1 yıllık rastgele OHLC verisi üretir,
pandas-ta-openbb kütüphanesini kullanarak RSI, SMA ve MACD
 göstergelerini hesaplar. Her gösterge için hesaplama süresi
``time.perf_counter`` ile ölçülür. Sonuçlar hem konsola yazdırılır
hem de ``benchmarks/README.md`` dosyasındaki karşılaştırma tablosu
güncellenir.

Kullanım:
    python benchmarks/compare_speed.py

Çıktı:
    - Konsola süre bilgileri basılır.
    - ``benchmarks/README.md`` içinde ``Göstergeler için Performans
      Karşılaştırması`` tablosu güncellenir.
"""

from __future__ import annotations

import importlib.metadata  # noqa: F401  # gerekli: pandas_ta icin
import time
from pathlib import Path

import numpy as np
import pandas as pd
import pandas_ta as ta


def generate_data(
    num_stocks: int = 1000, periods: int = 252
) -> dict[str, pd.DataFrame]:
    """Rastgele OHLC verisi üret."""
    dates = pd.date_range(end=pd.Timestamp.today(), periods=periods, freq="B")
    data: dict[str, pd.DataFrame] = {}
    for i in range(num_stocks):
        open_p = np.random.uniform(10, 100, size=periods)
        close = open_p + np.random.normal(scale=1, size=periods)
        high = np.maximum(open_p, close) + np.random.uniform(0, 2, size=periods)
        low = np.minimum(open_p, close) - np.random.uniform(0, 2, size=periods)
        volume = np.random.randint(1_000, 10_000, size=periods)
        df = pd.DataFrame(
            {
                "open": open_p,
                "high": high,
                "low": low,
                "close": close,
                "volume": volume,
            },
            index=dates,
        )
        data[f"STK{i:04d}"] = df
    return data


def time_indicator(name: str, func) -> float:
    """Bir gösterge fonksiyonunun çalışma süresini ölç."""
    start = time.perf_counter()
    func()
    return time.perf_counter() - start


def benchmark_indicators(data: dict[str, pd.DataFrame]) -> dict[str, float]:
    """RSI, SMA ve MACD hesaplama sürelerini ölç."""

    def run_rsi() -> None:
        for df in data.values():
            ta.rsi(df["close"])

    def run_sma() -> None:
        for df in data.values():
            ta.sma(df["close"])

    def run_macd() -> None:
        for df in data.values():
            ta.macd(df["close"])

    return {
        "RSI": time_indicator("RSI", run_rsi),
        "SMA": time_indicator("SMA", run_sma),
        "MACD": time_indicator("MACD", run_macd),
    }


def update_readme(results: dict[str, float]) -> None:
    """README dosyasındaki tabloyu güncelle."""
    readme = Path(__file__).with_name("README.md")
    table_lines = [
        "## Göstergeler için Performans Karşılaştırması",
        "",
        "| Gösterge | Süre (s) |",
        "| --- | --- |",
    ] + [f"| {k} | {v:.4f} |" for k, v in results.items()]

    if readme.exists():
        content = readme.read_text(encoding="utf-8")
    else:
        content = ""
    marker = "## Göstergeler için Performans Karşılaştırması"
    if marker in content:
        content = content.split(marker)[0].rstrip()
    content = content + "\n\n" + "\n".join(table_lines) + "\n"
    readme.write_text(content, encoding="utf-8")


def main() -> None:
    data = generate_data()
    results = benchmark_indicators(data)
    for k, v in results.items():
        print(f"{k} süresi: {v:.4f} s")
    update_readme(results)


if __name__ == "__main__":
    main()
