# Google Colab Hızlı Başlangıç

> Bu dosya **yalnızca Google Colab** içindir; buradaki `/content/...` yolları Colab'a özeldir.

Aşağıdaki hücreler Colab ortamında projeyi kurar, ortamı doğrular ve örnek bir tarama çalıştırır:

```python
# pip kurulumu
%pip install -q -r requirements_colab.txt -c constraints.txt --only-binary=:all:

%cd /content/finansal-analiz-sistemi
%env PYTHONPATH=/content/finansal-analiz-sistemi
!mkdir -p raporlar
```

## Konsol Çıktılarını Loglama

```python
import logging
from backtest.logging_utils import setup_logger
setup_logger()
!echo "Kurulum başlıyor" | tee -a loglar/colab_shell.log
!pip install -r requirements_colab.txt 2>&1 | tee -a loglar/colab_shell.log
!pytest -q 2>&1 | tee -a loglar/colab_shell.log
```

> `tee -a` komutu hem ekrana hem dosyaya yazdırır.

## Ortam Doğrulama

```python
!python tools/verify_env.py
```

## Örnek Tarama

```python
!python -m backtest.cli scan-range --config config/colab_config.yaml \
  --start 2025-03-07 --end 2025-03-11 \
  --holding-period 1 --transaction-cost 0.0005

!ls -la raporlar | head
```

> Excel okuma/yazma için gerekli `openpyxl` ve `XlsxWriter` paketleri `requirements_colab.txt` içinde yer alır.
> Tek veri kaynağı proje içindeki `data/` dizinidir; CLI'da `--excel-dir` parametresi yoktur.
> Varsayılan akış haricî indirme yapmaz; indirme için `--allow-download` veya `ALLOW_DOWNLOAD=1` gerekir.
> Spacy, fastai ve fastdownload bağımlılıkları kaldırılmıştır.

## İsim normalizasyonu

Veri dosyalarındaki ve filtre ifadelerindeki tüm sütun isimleri otomatik olarak
`lower_snake_case` biçimine dönüştürülür. Örneğin kullanıcı `EMA20` ya da
`ema-20` yazsa bile sistem bunu `ema_20` olarak yorumlar. Bu sayede veri
kaynakları ve filtreler arasında tutarlılık sağlanır.

İsteğe bağlı olarak testleri çalıştırmak için:

```python
%pip install -q -r requirements-dev.txt -c constraints.txt --only-binary=:all:
!pytest -q
```

## Veri İndirme Örneği (opsiyonel)

```python
!python -m backtest.cli fetch-range --symbols DEMO --start 2024-01-01 --end 2024-01-05 --provider stub
```
