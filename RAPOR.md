### Depo durumu
- `ls -a` komutunun çıktısı depo kök dizininde sadece `.git` klasörünün bulunduğunu, başka dosya olmadığını gösteriyor
- `git status` çıktısı “nothing to commit, working tree clean” diyerek depoda izlenen ya da izlenmeyen dosya olmadığını doğruluyor

### Sonuç
Depo, `.git` klasörü dışında hiçbir dosya içermiyor; yani tüm kaynak dosyaları tamamen silinmiş durumda.

### Testing
- `ls -a`
- `git status`
