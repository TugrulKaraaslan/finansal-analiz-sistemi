import utils.error_map as em


def test_get_reason_hint_value_error():
    reason, hint = em.get_reason_hint(ValueError("bad"))
    assert reason == "Geçersiz Değer"
    assert hint == "Parametreleri kontrol edin"
