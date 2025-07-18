"""Unit tests for option_guard."""

import pandas as pd

from utils.pandas_option_safe import ensure_option, option_context


def test_ensure_option_no_error():
    """Ensure option setting does not raise even if the option is missing."""
    ensure_option("future.no_silent_downcasting", True)
    try:
        val = pd.get_option("future.no_silent_downcasting")
    except (AttributeError, KeyError, pd.errors.OptionError):
        return
    assert val is True


def test_option_context_valid_resets():
    """Değişken bir pandas seçeneği doğru şekilde geçici olarak ayarlanmalı."""
    opt = "display.expand_frame_repr"
    original = pd.get_option(opt)
    with option_context(opt, not original):
        assert pd.get_option(opt) is (not original)
    assert pd.get_option(opt) is original


def test_option_context_ignores_invalid():
    """Olmayan bir seçenek hataya yol açmamalı."""
    with option_context("does.not.exist", True):
        assert True
