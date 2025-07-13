"""Tests ensuring :mod:`config` exposes required indicators."""


def test_config_has_core_indicators():
    """Check that ``CORE_INDICATORS`` exists and is not empty."""
    from finansal_analiz_sistemi import config as cfg

    # Does it exist?
    assert hasattr(cfg, "CORE_INDICATORS"), "config.py'de CORE_INDICATORS YOK!"
    # Is it a list?
    assert isinstance(cfg.CORE_INDICATORS, list), "CORE_INDICATORS bir liste değil!"
    # Is it non-empty?
    assert len(cfg.CORE_INDICATORS) > 0, "CORE_INDICATORS listesi boş!"
