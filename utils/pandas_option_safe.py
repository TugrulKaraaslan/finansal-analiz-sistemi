"""Helper functions to safely set pandas options across versions.

Unknown options are ignored instead of raising ``OptionError``.
"""

from collections.abc import Iterator
from contextlib import contextmanager, nullcontext

import pandas as pd


def ensure_option(name: str, value) -> None:
    """Attempt to set a pandas option when available.

    Unknown options are silently ignored so the helper works across
    pandas versions without raising :class:`OptionError`.

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
    """Temporarily set a pandas option if it exists.

    Args:
        name (str): Option name.
        value: Option value.

    Yields:
        None.
    """
    try:
        ctx = pd.option_context(name, value)
    except (AttributeError, KeyError, pd.errors.OptionError):
        ctx = nullcontext()
    try:
        with ctx:
            yield
    except (AttributeError, KeyError, pd.errors.OptionError):
        yield
