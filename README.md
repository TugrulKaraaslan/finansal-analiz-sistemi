# Finansal Parquet Cache Sistemi

[![CI](https://github.com/OWNER/REPO/actions/workflows/ci.yml/badge.svg)](https://github.com/OWNER/REPO/actions/workflows/ci.yml)

```bash
# otomatik kurulum
bash scripts/install.sh

# veya manuel kurulum
pip install -r requirements.txt                  # temel paketler
# OpenBB için:
pip install openbb pandas-ta-openbb
# Colab kullanıyorsanız: pip install -r requirements-colab.txt
pip install -r requirements-dev.txt             # test ve geliştirme araçları
pre-commit install                              # sürüm tutarlılığını kontrol eder
python -m finansal.cli --help
python run.py --help
python -m finansal_analiz_sistemi --help
```

 Örnek kullanım:

```bash
python -m finansal.cli --csv veri/prices.csv --log-level DEBUG
python -m finansal_analiz_sistemi.cli --dosya veri/prices.csv
```

## OpenBB Uyumluluğu

Bu proje artık OpenBB ile uyumludur. Eski pandas-ta desteği kaldırıldı.

### Önemli Değişiklikler
- pandas-ta fonksiyonlarının yerine `openbb_missing.py` aracılığıyla OpenBB çağrıları kullanılır.
- `requirements.txt` dosyasında `openbb` ve `pandas-ta-openbb` paketleri yer alır.
- Eski pandas-ta tabanlı testler güncellendi veya kaldırıldı.
- Teknik analiz fonksiyonlarının tamamı OpenBB arayüzüne geçirilmiştir.

### Rollback (Geri Alma)
1. `requirements.txt` içinde `pandas-ta-openbb` satırını `pandas-ta==0.3.14b0` ile değiştirin.
2. `openbb_missing.py` yerine eski pandas-ta fonksiyonlarını içeren modülleri geri yükleyin.
3. Testleri tekrar çalıştırarak uyumluluğu doğrulayın.

## Son Benchmark Sonucu
En son calisma suresi: 0.5397 saniye

## Benchmark Çalıştırma
`benchmarks/benchmark.py` betiği bir milyon rasgele sayı toplayarak süreyi ölçer.
Yerelde çalıştırmak için:

```bash
python benchmarks/benchmark.py
```

GitHub Actions üzerindeki [Benchmark iş akışı](.github/workflows/benchmark.yml) her push ve pull request'te bu betiği çağırır, oluşan `benchmark_output.txt` dosyasını doğrular ve çıktıyı bir artefakt olarak yükler.
