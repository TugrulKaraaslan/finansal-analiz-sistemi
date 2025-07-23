import utils.error_map as em


def test_get_reason_hint_value_error():
    reason, hint = em.get_reason_hint(ValueError("bad"))
    assert reason == "Geçersiz Değer"
    assert hint == "Parametreleri kontrol edin"


def test_get_reason_hint_file_not_found():
    reason, hint = em.get_reason_hint(FileNotFoundError("missing"))
    assert reason == "Dosya Bulunamadı"
    assert hint == "Geçerli bir dosya yolu belirtin"


def test_get_reason_hint_not_implemented():
    reason, hint = em.get_reason_hint(NotImplementedError())
    assert reason == "Desteklenmiyor"
    assert hint == "İlgili paketi kurun veya güncelleyin"


def test_get_reason_hint_type_error():
    reason, hint = em.get_reason_hint(TypeError("bad type"))
    assert reason == "Tip Hatası"
    assert hint == "Parametre tiplerini kontrol edin"
