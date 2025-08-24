from __future__ import annotations

import pandas as pd

from .cross import cross_down as _cross_down
from .cross import cross_over, cross_under
from .cross import cross_up as _cross_up


def build_env(df: pd.DataFrame):
    def _env_cross_up(a, b):
        s1 = df[a]
        if isinstance(b, str) and b in df:
            s2 = df[b]
            out = _cross_up(s1, s2)
        else:
            out = cross_over(s1, b)
        out.iloc[-1] = False
        return out.fillna(False)

    def _env_cross_down(a, b):
        s1 = df[a]
        if isinstance(b, str) and b in df:
            s2 = df[b]
            if s2.nunique() == 1:
                level = s2.iloc[0]
                out = (s1.shift(1) > level) & (s1 <= level)
            else:
                out = _cross_down(s1, s2)
        else:
            out = (s1.shift(1) > b) & (s1 <= b)
        out.iloc[-1] = False
        return out.fillna(False)

    env = {"cross_up": _env_cross_up, "cross_down": _env_cross_down}
    for c in df.columns:
        env[c] = df[c]
    return env


__all__ = ["build_env"]
