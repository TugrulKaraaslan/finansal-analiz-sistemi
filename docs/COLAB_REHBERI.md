# Google Colab — Kurulum & Çalıştırma Rehberi (2025)

Bu belge, **finansal_analiz_sistemi** deposunu Google Colab ortamında
"sıfırdan" kurup tüm testleri ve `run.py` betiğini çalıştırmak için güncel
adımları içerir. Her komut ayrı hücrede kopyala–yapıştır yapılacak şekilde
verilmiştir.

> **Not:** Çıktılar varsayılan olarak `raporlar/` klasörüne yazılır.

---

## 0. OpenBB Kurulumu
```bash
!pip install -q pandas-ta-openbb
```

## 1. (İsteğe bağlı) Google Drive Bağlama
Aşağıdaki komutla Drive'ı bağlayarak raporları kalıcı saklayabilirsiniz.
```python
from google.colab import drive
drive.mount('/content/drive')
```

---

## 2. Depoyu Klonla
```bash
!git clone https://github.com/TugrulKaraaslan/finansal-analiz-sistemi.git
%cd finansal-analiz-sistemi
```
(Özel repo ise URL'nin başına `https://<TOKEN>@` ekleyin.)

---

## 3. Kütüphaneleri Kur (Sürüm Sabitleme)
```bash
!bash scripts/install.sh
!pip install -e .
```
`requirements-dev.txt` dosyası, isteğe bağlı test bağımlılıklarını (örneğin
**pyarrow**) da içerir. Bu adım proje ve test bağımlılıklarını tam sürüm
uyumuyla kurar.

---

## 4. PYTHONPATH Ayarı
```python
import sys, pathlib
proj_path = pathlib.Path.cwd().resolve()
if str(proj_path) not in sys.path:
    sys.path.append(str(proj_path))
    print('PYTHONPATH ➕', proj_path)
```
Bu ayar yerel modüllerin (`import finansal_analiz_sistemi` vb.) sorunsuz
çağrılmasını sağlar.

---

## 5. (İsteğe Bağlı) Colab Renkli Log
```python
from finansal_analiz_sistemi import config
config.IS_COLAB = True
```
Renkli log çıktısı için `IS_COLAB` bayrağını açabilirsiniz.

---

## 6. Testleri Çalıştır
```bash
!pytest -q
```
Tüm testlerin geçtiğinden emin olun. Hata durumunda log dosyalarına bakın.

---

## 7. Backtest Başlatma
```bash
!python run.py \
    --tarama 07.03.2025 \
    --satis 10.03.2025 \
    --output raporlar/sonuc.xlsx \
    --log-level INFO
```
`--output` parametresiyle rapor dosyasının kaydedileceği yolu belirtin.
Drive kullanıyorsanız `/content/drive/MyDrive/` altını verebilirsiniz.

---

## 8. Raporu İndir
```python
from google.colab import files
files.download('raporlar/sonuc.xlsx')
```
Drive bağladıysanız dosya doğrudan Drive'da oluşacaktır.

---

## 9. Log İnceleme ve Hata Analizi
Aşağıdaki komutlar son log mesajlarını görmenizi sağlar.
```bash
!cat loglar/*.log | tail -n 100
```
Tüm logu görmek isterseniz:
```bash
!cat loglar/*.log
```
Yaygın hatalar ve olası çözümler için tablo:

| Mesaj | Sebep | Çözüm |
|-------|-------|-------|
| `ModuleNotFoundError` | Eksik paket | `pip install -r requirements-colab.txt` adımını kontrol edin |
| `KeyError: 'filtre_kodu'` | Yanlış/eksik veri dosyası | Veri yollarını ve tarihleri gözden geçirin |
| `Permission denied` | Drive dosyası salt okunur | Dosya izinlerini ve konumu kontrol edin |

---

## 10. Disk Temizliği
```bash
!rm -rf ~/.cache/pip
!find raporlar -type f -name '*.xlsx' -mtime +7 -delete
```
Geçici dosyaları ve eski raporları silerek Colab kotasını yönetebilirsiniz.

---

Hepsi bu kadar! Bu rehberle Colab üzerinde kararlı ve otomatik bir şekilde
testleri çalıştırıp backtest raporlarınızı üretebilirsiniz.
