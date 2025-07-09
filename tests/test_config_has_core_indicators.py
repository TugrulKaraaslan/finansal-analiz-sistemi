"""Tests ensuring :mod:`config` exposes required indicators."""


def test_config_has_core_indicators():
    """
    config.py dosyasında CORE_INDICATORS sabiti var mı ve içi boş değil mi?
    Hata varsa, net Türkçe açıklama verir.
    """
    from finansal_analiz_sistemi import config as cfg

    # Tanımlı mı?
    assert hasattr(cfg, "CORE_INDICATORS"), "config.py'de CORE_INDICATORS YOK!"
    # Liste mi?
    assert isinstance(cfg.CORE_INDICATORS, list), "CORE_INDICATORS bir liste değil!"
    # Boş mu?
    assert len(cfg.CORE_INDICATORS) > 0, "CORE_INDICATORS listesi boş!"
