"""Stubs for missing OpenBB functionality.

This module defines placeholder functions for pandas-ta features not yet
supported by OpenBB. Each function simply raises ``NotImplementedError``
to signal that an equivalent implementation is unavailable.
"""

from __future__ import annotations


def tema(*_args, **_kwargs):
    """Placeholder for :func:`pandas_ta.tema`."""
    raise NotImplementedError("openbb equivalent for 'tema' is missing")


def Strategy(*_args, **_kwargs):  # noqa: N802
    """Placeholder for :class:`pandas_ta.Strategy`."""
    raise NotImplementedError("openbb equivalent for 'Strategy' is missing")


def strategy(*_args, **_kwargs):
    """Placeholder for ``DataFrame.ta.strategy``."""
    raise NotImplementedError("openbb equivalent for 'strategy' is missing")


def psar(*_args, **_kwargs):
    """Placeholder for ``DataFrame.ta.psar`` or :func:`pandas_ta.psar`."""
    raise NotImplementedError("openbb equivalent for 'psar' is missing")


def ichimoku(*_args, **_kwargs):
    """Placeholder for :func:`pandas_ta.ichimoku`."""
    raise NotImplementedError("openbb equivalent for 'ichimoku' is missing")


def rsi(*_args, **_kwargs):
    """Placeholder for :func:`pandas_ta.rsi`."""
    raise NotImplementedError("openbb equivalent for 'rsi' is missing")


def macd(*_args, **_kwargs):
    """Placeholder for :func:`pandas_ta.macd`."""
    raise NotImplementedError("openbb equivalent for 'macd' is missing")


def stochrsi(*_args, **_kwargs):
    """Placeholder for :func:`pandas_ta.stochrsi`."""
    raise NotImplementedError("openbb equivalent for 'stochrsi' is missing")


MISSING_FUNCTIONS = [
    "tema",
    "Strategy",
    "strategy",
    "psar",
    "ichimoku",
    "rsi",
    "macd",
    "stochrsi",
]
