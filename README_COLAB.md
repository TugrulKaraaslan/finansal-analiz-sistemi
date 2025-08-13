# Google Colab Hızlı Başlangıç

Aşağıdaki hücre Colab ortamında projeyi kurar ve örnek bir tarama çalıştırır:

```python
# pip kurulumu
%pip install -q -r requirements_colab.txt -c constraints.txt --only-binary=:all: --no-binary=pandas-ta
# Uygun wheel bulunamazsa veya pandas_ta uyumsuzluğu olursa:
%pip install "numpy<2.0" "pandas<2.2" pandas-ta==0.3.14b0

%cd /content/finansal-analiz-sistemi
%env PYTHONPATH=/content/finansal-analiz-sistemi
!mkdir -p raporlar

!python -m backtest.cli scan-range --config config/colab_config.yaml \
  --start 2025-03-07 --end 2025-03-11 \
  --holding-period 1 --transaction-cost 0.0005

!ls -la raporlar | head
```

## İsim normalizasyonu

Veri dosyalarındaki ve filtre ifadelerindeki tüm sütun isimleri otomatik olarak
`lower_snake_case` biçimine dönüştürülür. Örneğin kullanıcı `EMA20` ya da
`ema-20` yazsa bile sistem bunu `ema_20` olarak yorumlar. Bu sayede veri
kaynakları ve filtreler arasında tutarlılık sağlanır.

Desteklenen varyantların kanonik karşılıklarını görmek veya `filters.csv`
dosyasındaki sorguları düzeltmek için:

```bash
python tools/audit_names.py --write-fixes
```

Bu komut örnek veri dosyasındaki ham → kanonik sütun adlarını ve filtrelerdeki
isim dönüşümlerini raporlar; `filters_fixed.csv` dosyasını üretir.

İsteğe bağlı olarak testleri çalıştırmak için:

```python
%pip install -q -r requirements_dev.txt -c constraints.txt --only-binary=:all: --no-binary=pandas-ta
!pytest -q
```
