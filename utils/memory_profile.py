"""Context manager to record process memory usage.

Using ``with mem_profile():`` appends a ``timestamp,rss,diff`` line to
``reports/memory_profile.csv`` so memory consumption can be reviewed
after execution. The ``MemoryProfile`` class provides the actual
implementation while ``mem_profile`` is kept as a backwards compatible
alias. The recorded values represent the RSS at the end of the context
and the difference to the starting RSS, not the true peak usage.
"""

import os
import time
from dataclasses import dataclass, field
from pathlib import Path
from types import TracebackType
from typing import Optional, Type

import psutil

__all__ = ["MemoryProfile", "mem_profile"]


@dataclass
class MemoryProfile:
    """Context manager that records process memory usage to disk."""

    path: Path = field(default_factory=lambda: Path("reports/memory_profile.csv"))
    proc: psutil.Process = field(init=False)
    start: int = field(init=False)

    def __post_init__(self) -> None:
        """Normalize the ``path`` attribute to a :class:`~pathlib.Path`."""
        self.path = Path(self.path)

    def __enter__(self) -> "MemoryProfile":
        """Start tracking process memory usage and return ``self``."""
        self.proc = psutil.Process(os.getpid())
        self.start = self.proc.memory_info().rss
        return self

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc: Optional[BaseException],
        tb: Optional[TracebackType],
    ) -> bool:
        """Log current RSS memory usage and allow exception propagation.

        Parameters
        ----------
        exc_type : Optional[Type[BaseException]]
            Exception class if an error occurred.
        exc : Optional[BaseException]
            Raised exception instance, if any.
        tb : Optional[TracebackType]
            Traceback object associated with ``exc``.

        Returns
        -------
        bool
            ``False`` so any exception is re-raised by the context manager.
        """
        end_rss = self.proc.memory_info().rss
        diff = end_rss - self.start
        self.path.parent.mkdir(exist_ok=True)
        with self.path.open("a", encoding="utf-8") as f:
            f.write(f"{time.time()},{end_rss},{diff}\n")
        return False


mem_profile = MemoryProfile
