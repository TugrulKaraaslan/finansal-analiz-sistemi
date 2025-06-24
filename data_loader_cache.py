# data_loader_cache.py
import os

import pandas as pd


class DataLoaderCache:
    """Basit dosya okuma önbelleği.

    Bu sınıf, CSV ve Excel dosyalarının diskten her okunuşunda tekrar
    yüklenmesini önlemek için basit bir bellek içi önbellek tutar. ``load_csv``
    ve ``load_excel`` metodları aynı dosya yolu için daha önce yüklenmiş bir
    nesne varsa bunu döndürür, aksi halde dosyayı okuyup önbelleğe ekler.

    Args:
        logger (logging.Logger, optional): İşlemler hakkında bilgi vermek için
            kullanılacak logger nesnesi.
    """

    def __init__(self, logger=None):
        self.loaded_data = {}
        self.logger = logger

    def load_excel(self, filepath: str, **kwargs) -> pd.ExcelFile:
        key = (os.path.abspath(filepath), "__excel__")
        if key in self.loaded_data:
            if self.logger:
                self.logger.debug(f"Cache hit: {key}")
            return self.loaded_data[key]

        try:
            xls = pd.ExcelFile(filepath, **kwargs)
            self.loaded_data[key] = xls
            if self.logger:
                self.logger.info(f"ExcelFile yüklendi: {filepath}")
            return xls
        except Exception as e:
            if self.logger:
                self.logger.error(f"ExcelFile yükleme hatası: {filepath}: {e}")
            raise

    def load_csv(self, filepath: str, **kwargs) -> pd.DataFrame:
        key = (os.path.abspath(filepath), "__csv__")
        if key in self.loaded_data:
            if self.logger:
                self.logger.debug(f"Cache hit: {key}")
            return self.loaded_data[key]

        try:
            df = pd.read_csv(filepath, **kwargs)
            self.loaded_data[key] = df
            if self.logger:
                self.logger.info(f"CSV yüklendi: {filepath}")
            return df
        except Exception as e:
            if self.logger:
                self.logger.error(f"CSV yükleme hatası: {filepath}: {e}")
            raise
