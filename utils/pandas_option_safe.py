"""Helper functions to safely set pandas options across versions.

Unknown options are ignored instead of raising ``OptionError``.
"""

from collections.abc import Iterator
from contextlib import contextmanager
from typing import Any

import pandas as pd


def ensure_option(name: str, value: Any) -> None:
    """Attempt to set a pandas option when available.

    Unknown options are silently ignored so the helper works across
    pandas versions without raising :class:`OptionError`.

    Args:
        name (str): Option name.
        value (Any): Option value.
    """
    try:
        pd.set_option(name, value)
    except (AttributeError, KeyError, pd.errors.OptionError):
        # Option missing in older pandas versions; skip silently
        pass


@contextmanager
def option_context(name: str, value: Any) -> Iterator[None]:
    """Temporarily set a pandas option if it exists.

    Args:
        name (str): Option name.
        value (Any): Option value.

    Yields:
        None.
    """
    try:
        with pd.option_context(name, value):
            yield
    except (AttributeError, KeyError, pd.errors.OptionError):
        yield
