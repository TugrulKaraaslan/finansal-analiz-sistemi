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

> **Not:** Google Colab ortamı `pandas` 2.x ile gelir. Bu proje ise
> `pandas==1.5.3` kullanır. Paketleri doğru sürümlerle yeniden kurmak için
> `--force-reinstall` ve `--no-cache-dir` bayraklarını kullanmanız önerilir.

1. Depoyu klonlayın ve klasöre geçin.
2. Gereken paketleri yeniden kurun.
3. Testleri ve örnek çalıştırmayı yapın.

```bash
!git clone https://github.com/<KULLANICI>/finansal-analiz-sistemi.git
%cd finansal-analiz-sistemi
!pip install --force-reinstall --no-cache-dir -r requirements.txt
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


## Otomatik Sağlık Raporu
Backtest tamamlandığında son log dosyası ve üretilen rapor kullanılarak ek bir "sağlık" raporu oluşturulur. Bu Excel dosyası `sağlık_raporu_<tarih>.xlsx` adıyla çalışma dizinine kaydedilir.
