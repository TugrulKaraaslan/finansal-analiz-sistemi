# Finansal Parquet Cache Sistemi

```bash
pip install -r requirements.txt  # veya Colab için requirements-colab.txt
pip install -r requirements-dev.txt  # Parquet testleri için pyarrow içerir
python -m finansal.cli --help
python run.py --help
```

Örnek kullanım:

```bash
python -m finansal.cli --csv veri/prices.csv --log-level DEBUG
```
