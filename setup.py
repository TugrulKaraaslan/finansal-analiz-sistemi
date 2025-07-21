"""Setuptools entry point for packaging the project.

This file exists for compatibility with packaging tools that rely on
``setup.py`` even when ``pyproject.toml`` is present.
"""

from __future__ import annotations

from setuptools import setup

if __name__ == "__main__":
    setup()
