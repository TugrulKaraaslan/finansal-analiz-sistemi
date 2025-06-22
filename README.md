# finansal-analiz-sistemi
[![CI](https://github.com/owner/finansal-analiz-sistemi/actions/workflows/ci.yml/badge.svg)](https://github.com/owner/finansal-analiz-sistemi/actions/workflows/ci.yml)
[![Coverage](https://img.shields.io/badge/coverage-91%25-brightgreen.svg)](https://github.com/owner/finansal-analiz-sistemi/actions/workflows/ci.yml)
ChatGPT ile geliştirilen backtest otomasyon projesi

## Installation
```bash
pip install finansal-analiz-sistemi[pyarrow]   # enables Parquet & fast tests
```

## Configuration

| Key                   | Default | Description                                    |
| --------------------- | ------- | ---------------------------------------------- |
| `max_filter_depth`    | `7`     | Recursion guard for nested filter expressions. |
| `output_format`       | `xlsx`  | Report output (`csv`/`xlsx`).                  |
| `log_simple` env flag | `1`     | Set to `0` for Rich color logs (Colab).        |

Sample **config.yml** snippet:

```yaml
max_filter_depth: 9
output_format: csv      # override default
```


## Destek Matrisi

| Tier | Pandas | NumPy |
|------|--------|-------|
| 🟢 LTS | 2.2.2 | 2.0.2 |
| 🟡 Legacy | 1.5.3 | 1.26.4 |

## Geliştirme Ortamı Kurulumu

1. Python 3.11+ yüklü olduğundan emin olun.
2. Sanal ortam oluşturun ve etkinleştirin:
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```
3. Gerekli paketleri yükleyin:
   ```bash
   pip install -r requirements.txt
   ```
4. `pre-commit` kurulumunu yapın ve git kancalarını etkinleştirin:
   ```bash
   pip install pre-commit
   pre-commit install
   ```

## Sürüm Pinleme

Projede kullanılan paketlerin sürüm kilitlemesi için [pip-tools](https://pypi.org/project/pip-tools/) kullanılabilir. Aşağıdaki komut akışı `requirements.txt` dosyasını güncelleyerek kararlı bir ortam sağlar:

```bash
scripts/lock_requirements.sh
```


## Testlerin Çalıştırılması

Projede bulunan birim testlerini çalıştırmak için:
```bash
pytest -q -m "not slow" --cov .
```

## Google Colab Hızlı Başlangıç

1. Depoyu klonlayın ve klasöre geçin.
2. Gereken paketleri kurun.
3. Testleri ve örnek çalıştırmayı yapın.

```bash
!git clone https://github.com/<KULLANICI>/finansal-analiz-sistemi.git
%cd finansal-analiz-sistemi
!pip install -r requirements.txt
!pytest -q
!python -m finansal_analiz_sistemi
```

## Rapor oluşturma (hızlı yöntem)

```bash
pip install xlsxwriter
```

## Docker ile çalıştırma

```bash
docker build -t finansal_analiz .
docker run --rm finansal_analiz
```

### LOG_SIMPLE=1 düz log için
`LOG_SIMPLE=1` değeri ayarlandığında konsol çıktısı renkli olmayıp basit biçimde görünür.

## Komut Satırı Kullanımı

Komut satırından çalıştırmak için `python -m finansal_analiz_sistemi` komutu kullanılır. Aşağıdaki parametreleri kabul eder:

```bash
python -m finansal_analiz_sistemi --tarama 01.01.2025 --satis 05.01.2025 [--gui]
python -m finansal_analiz_sistemi --tarama 2025-03-07 --satis 2025-03-10
```
(GG.AA.YYYY biçimi de desteklenir)

* `--tarama` ve `--satis` tarihleri `yyyy-mm-dd` formatındadır.
* `--gui` verildiğinde sonuçlar basit bir Streamlit arayüzünde görüntülenir.
* Filtre dosyaları CSV (`;` ayracıyla), Excel (.xlsx/.xls - ilk sayfa) veya Parquet (.parquet) formatında olabilir.

## Usage
```python
from finansal_analiz_sistemi.data_loader import yukle_filtre_dosyasi
df = yukle_filtre_dosyasi("filters.xlsx")
```


## Otomatik Sağlık Raporu
Backtest tamamlandığında son log dosyası ve üretilen rapor kullanılarak ek bir "sağlık" raporu oluşturulur. Bu Excel dosyası `sağlık_raporu_<tarih>.xlsx` adıyla çalışma dizinine kaydedilir.

## Changelog
- Ichimoku hatası giderildi.
- Hatalar sekmesi eklendi.
- Satış tarihi veri yoksa tarih kaydırma.
- Excel BarChart + boyut küçültme.
- CI: 'pip install .[dev]' → 'pip install -r requirements.txt' olarak düzeltildi.
- Filtre derinliği `max_filter_depth` ayarıyla yönetilir (varsayılan 7).
