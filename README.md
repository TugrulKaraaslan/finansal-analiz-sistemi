 # Finansal Parquet Cache Sistemi
 
```bash
pip install -r requirements.txt                  # temel paketler
# Colab kullanıyorsanız: pip install -r requirements-colab.txt
pip install -r requirements-dev.txt             # test ve geliştirme araçları
python -m finansal.cli --help
python run.py --help
```
 
 Örnek kullanım:
 
 ```bash
 python -m finansal.cli --csv veri/prices.csv --log-level DEBUG
 ```
