# Colab Kurulum & Çalıştırma (v1.3.2)

Bu rehber, Google Colab üzerinde projeyi sıfırdan hatasız çalıştırmanız için hazırlanmıştır.

## 1) Gereksinimleri sabit sürümlerle kur
```python
!pip install -q -U pip
req = """
numpy==1.26.4
pandas==2.2.2
pandas-ta==0.3.14b0
pyarrow==21.0.0
openpyxl
xlsxwriter
loguru
tqdm
click
pydantic
""".strip()
open('/content/requirements_colab.txt','w').write(req)
!pip install -q --force-reinstall -r /content/requirements_colab.txt
```

## 2) Runtime'ı yeniden başlat
```python
import os, signal; os.kill(os.getpid(), 9)
```

## 3) Drive'ı bağla ve ZIP'i /content'e kopyala (Drive kullanıyorsanız)
```python
from google.colab import drive
drive.mount('/content/drive')

# Gerçek konumunuza göre yolu düzenleyin
!cp '/content/drive/MyDrive/backtest_project_v1_3_2_full.zip' /content/
```

## 4) Projeyi aç (veya elinizdeki zip'i yükleyip açın)
```python
!unzip -o /content/backtest_project_v1_3_2_full.zip -d /content/
%cd /content/backtest_project
!mkdir -p raporlar
```

## 5) CLI yardımı ve test
```python
!PYTHONPATH=. python -m backtest.cli --help
!PYTHONPATH=. python -m backtest.cli scan-range --help
```

## 6) Hızlı çalışma örnekleri
```python
# Çok gün aralığı (örnek)
!PYTHONPATH=. python -m backtest.cli scan-range       --start 2025-03-07 --end 2025-03-11       --data-path ./Veri       --filter-path ./filters.csv       --output-dir ./raporlar

# Tek gün (örnek)
!PYTHONPATH=. python -m backtest.cli scan-day       --date 2025-03-07       --data-path ./Veri       --filter-path ./filters.csv       --output-dir ./raporlar
```

### Notlar
- `./Veri` klasörü altında 13 Excel dosyası (çoklu sheet'li) bulunmalıdır.
- `filters.csv` kök dizinde olmalıdır.
- Çıktılar `./raporlar/` altına yazılır (Excel/CSV).
- BIST farkı, ortalama getiri ve win-rate hesapları raporlarda mevcuttur.
