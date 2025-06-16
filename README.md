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

## Google Colab Hızlı Başlangıç

1. Depoyu klonlayın ve klasöre geçin.
2. Gereken paketleri kurun.
3. Testleri ve örnek çalıştırmayı yapın.

```bash
!git clone https://github.com/<KULLANICI>/finansal-analiz-sistemi.git
%cd finansal-analiz-sistemi
!pip install -r requirements.txt
!pytest -q
!python main.py
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

## Komut Satırı Kullanımı

Temel script `main.py` aşağıdaki parametreleri kabul eder:

```bash
python main.py --tarama 01.01.2025 --satis 05.01.2025 [--gui]
python main.py --tarama 2025-03-07 --satis 2025-03-10
```
(GG.AA.YYYY biçimi de desteklenir)

* `--tarama` ve `--satis` tarihleri `yyyy-mm-dd` formatındadır.
* `--gui` verildiğinde sonuçlar basit bir Streamlit arayüzünde görüntülenir.


## Otomatik Sağlık Raporu
Backtest tamamlandığında son log dosyası ve üretilen rapor kullanılarak ek bir "sağlık" raporu oluşturulur. Bu Excel dosyası `sağlık_raporu_<tarih>.xlsx` adıyla çalışma dizinine kaydedilir.

## Changelog
- Ichimoku hatası giderildi.
- Hatalar sekmesi eklendi.
- Satış tarihi veri yoksa tarih kaydırma.
- Excel BarChart + boyut küçültme.
- CI: 'pip install .[dev]' → 'pip install -r requirements.txt' olarak düzeltildi.
