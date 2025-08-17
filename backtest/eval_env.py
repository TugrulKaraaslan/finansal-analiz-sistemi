from __future__ import annotations
import pandas as pd
from .cross import cross_up, cross_down, cross_over, cross_under


def build_env(df: pd.DataFrame):
    env = {
        "CROSSUP": lambda a, b: cross_up(df[a], df[b]),
        "CROSSDOWN": lambda a, b: cross_down(df[a], df[b]),
        "CROSSOVER": lambda a, level: cross_over(df[a], level),
        "CROSSUNDER": lambda a, level: cross_under(df[a], level),
    }
    for c in df.columns:
        env[c] = df[c]
    return env


__all__ = ["build_env"]
