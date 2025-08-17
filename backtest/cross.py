import pandas as pd

def cross_up(s1: pd.Series, s2: pd.Series) -> pd.Series:
    return (s1.shift(1) <= s2.shift(1)) & (s1 > s2)

def cross_down(s1: pd.Series, s2: pd.Series) -> pd.Series:
    return (s1.shift(1) >= s2.shift(1)) & (s1 < s2)

def cross_over(s: pd.Series, level: float) -> pd.Series:
    return (s.shift(1) <= level) & (s > level)

def cross_under(s: pd.Series, level: float) -> pd.Series:
    return (s.shift(1) >= level) & (s < level)

__all__ = ["cross_up", "cross_down", "cross_over", "cross_under"]
