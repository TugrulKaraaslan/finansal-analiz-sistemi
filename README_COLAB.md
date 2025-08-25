# Google Colab Hızlı Başlangıç

> Bu dosya **yalnızca Google Colab** içindir; buradaki `/content/...` yolları Colab'a özeldir.

Aşağıdaki hücreler Colab ortamında projeyi kurar, ortamı doğrular ve örnek bir tarama çalıştırır:

```python
!python notebooks/colab_setup.py

%cd /content/finansal-analiz-sistemi
%env PYTHONPATH=/content/finansal-analiz-sistemi
!mkdir -p raporlar
```

> opencv gerekiyorsa: `pip install '.[cv]'`

## Konsol Çıktılarını Loglama

```python
import logging
from backtest.logging_utils import setup_logger
setup_logger()
!python notebooks/colab_setup.py
!pytest -q 2>&1 | tee -a loglar/colab_shell.log
```

> `notebooks/colab_setup.py` komutu paket kurulum çıktısını `loglar/colab_install.log` dosyasına yazar.

## Ortam Doğrulama

```python
!python tools/verify_env.py
```

## Örnek Tarama

```python
!python -m backtest.cli scan-range --config config/colab_config.yaml \
  --start 2025-03-07 --end 2025-03-11

!ls -la raporlar | head
```

> Excel okuma/yazma için gerekli `openpyxl` ve `XlsxWriter` paketleri bağımlılık setinde yer alır.
> Tek veri kaynağı proje içindeki `data/` dizinidir; CLI'da `--excel-dir` parametresi yoktur.
> Spacy, fastai ve fastdownload bağımlılıkları kaldırılmıştır.

## İsim normalizasyonu

Veri dosyalarındaki ve filtre ifadelerindeki tüm sütun isimleri otomatik olarak
`lower_snake_case` biçimine dönüştürülür. Örneğin kullanıcı `EMA20` ya da
`ema-20` yazsa bile sistem bunu `ema_20` olarak yorumlar. Bu sayede veri
kaynakları ve filtreler arasında tutarlılık sağlanır.

İsteğe bağlı olarak testleri çalıştırmak için:

```python
!make dev-setup
!pytest -q
```

## Veri İndirme Örneği (opsiyonel)

```python
!python -m backtest.cli fetch-range --symbols DEMO --start 2024-01-01 --end 2024-01-05 --provider stub
```
