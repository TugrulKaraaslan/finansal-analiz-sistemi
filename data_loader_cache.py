# data_loader_cache.py
import pandas as pd
import os

class DataLoaderCache:
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
