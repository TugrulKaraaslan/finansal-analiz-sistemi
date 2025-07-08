"""Helpers to safely set pandas options across versions."""

from collections.abc import Iterator
from contextlib import contextmanager

import pandas as pd


def ensure_option(name: str, value) -> None:
    """Attempt to set a pandas option if it exists."""
    try:
        pd.set_option(name, value)
    except (AttributeError, KeyError, pd.errors.OptionError):
        # Option missing in older pandas versions; skip silently
        pass


@contextmanager
def option_context(name: str, value) -> Iterator[None]:
    """Like ``pd.option_context`` but ignores unknown-option errors."""
    try:
        with pd.option_context(name, value):
            yield
    except (AttributeError, KeyError, pd.errors.OptionError):
        yield
