# Benchmark Hakkında

## Benchmark nasıl çalışır?
Bu dizindeki `benchmark.py` dosyası basit bir rasgele sayı toplama işlemi yaparak performans ölçer. Betiği yerel makinenizde `python benchmarks/benchmark.py` komutuyla veya GitHub Actions üzerindeki Benchmark iş akışıyla çalıştırabilirsiniz.

## Son performans çıktısı
Benchmark tamamlandığında sonuç `benchmark_output.txt` dosyasına yazılır ve aynı zamanda ekrana basılır.

## Olası hata/iyileştirme önerileri
- Farklı işlem yükleriyle daha gerçekçi testler oluşturabilirsiniz.
- Dosya oluşturulamazsa veya çalışma süresi beklenenden uzunsa iş akışı başarısız olur ve loglarda hata mesajı yer alır.
