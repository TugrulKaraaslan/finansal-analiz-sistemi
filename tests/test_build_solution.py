import filter_engine


def test_build_solution_missing_column():
    msg = "Eksik sütunlar: ema_10"
    out = filter_engine._build_solution("GENERIC", msg)
    assert out == '"ema_10" indikatörünü hesaplama listesine ekleyin.'


def test_build_solution_undefined_column():
    msg = "Tanımsız sütun/değişken: 'foo'"
    out = filter_engine._build_solution("GENERIC", msg)
    assert (
        out == 'Sorguda geçen "foo" sütununu veri setine ekleyin veya sorgudan çıkarın.'
    )


def test_build_solution_query_error():
    out = filter_engine._build_solution("QUERY_ERROR", "hata")
    assert out == "Query ifadesini pandas.query() sözdizimine göre düzeltin."


def test_build_solution_no_stock():
    out = filter_engine._build_solution("NO_STOCK", "")
    assert out == "Filtre koşullarını gevşetin veya tarih aralığını genişletin."
