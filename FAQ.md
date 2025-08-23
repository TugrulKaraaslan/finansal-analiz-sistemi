# FAQ

## Excel nereye konur?
Excel dosyaları proje kökünde `Veri/` klasörüne yerleştirilir. Farklı bir konum kullanmak için `config` dosyasındaki `excel_dir` alanını veya `EXCEL_DIR` ortam değişkenini ayarlayın.

## Fixtures nasıl üretilir?
Test için küçük örnek veri setlerini oluşturmak üzere:

```bash
make fixtures
```

## Alias neden uyarı veriyor?
Legacy kolon adları kullanıldığında, sistem bunları [docs/ALIAS_POLICY.md](docs/ALIAS_POLICY.md) politikasına göre kanonikleştirir ve uyarı mesajı gösterir.

## Golden nasıl güncellenir?
Test checksum'larını güncellemek için:

```bash
make golden
```
