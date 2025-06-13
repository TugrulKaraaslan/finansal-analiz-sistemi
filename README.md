# finansal-analiz-sistemi
[![CI](https://github.com/<your-username>/finansal-analiz-sistemi/actions/workflows/ci.yml/badge.svg)](https://github.com/<your-username>/finansal-analiz-sistemi/actions/workflows/ci.yml)
ChatGPT ile geliştirilen backtest otomasyon projesi

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

## Testlerin Çalıştırılması

Projede bulunan birim testlerini çalıştırmak için:
```bash
pytest -q
```

## Running in Google Colab

1. Clone the repository and move into the directory:
   ```python
   !git clone https://github.com/<your-username>/finansal-analiz-sistemi.git
   %cd finansal-analiz-sistemi
   ```
2. Install the dependencies together with `pytest`:
   ```python
   !pip install -r requirements.txt pytest
   ```
3. Run the unit tests:
    ```python
    !pytest -q
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

