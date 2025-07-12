"""Helpers to safely set pandas options across versions.

Unknown options are ignored instead of raising ``OptionError``.
"""

from collections.abc import Iterator
from contextlib import contextmanager

import pandas as pd


def ensure_option(name: str, value) -> None:
    """Attempt to set a pandas option if it exists.

    Args:
        name (str): Option name.
        value: Option value.
    """
    try:
        pd.set_option(name, value)
    except (AttributeError, KeyError, pd.errors.OptionError):
        # Option missing in older pandas versions; skip silently
        pass


@contextmanager
def option_context(name: str, value) -> Iterator[None]:
    """Like ``pd.option_context`` but ignore unknown-option errors.

    Args:
        name (str): Option name.
        value: Option value.

    Yields:
        None
    """
    try:
        with pd.option_context(name, value):
            yield
    except (AttributeError, KeyError, pd.errors.OptionError):
        yield
