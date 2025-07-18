import utils.error_map as em


def test_get_reason_hint_value_error():
    reason, hint = em.get_reason_hint(ValueError("bad"))
    assert reason == "Geçersiz Değer"
    assert hint == "Parametreleri kontrol edin"


def test_get_reason_hint_file_not_found():
    reason, hint = em.get_reason_hint(FileNotFoundError("missing"))
    assert reason == "Dosya Bulunamadı"
    assert hint == "Geçerli bir dosya yolu belirtin"
