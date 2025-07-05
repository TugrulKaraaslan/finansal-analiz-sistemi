import importlib
import importlib.util
import os

PKG_CONFIG_MODULE = "finansal_analiz_sistemi.config"

canonical_spec = importlib.util.find_spec(PKG_CONFIG_MODULE)
shadow_spec = importlib.util.find_spec("config")
if shadow_spec and canonical_spec and shadow_spec.origin != canonical_spec.origin:
    raise RuntimeError("Shadow config.py detected; use explicit package import")

config = importlib.import_module(PKG_CONFIG_MODULE)

APP_ENV = os.getenv("APP_ENV", "dev")
if APP_ENV == "prod":
    config.LOG_LEVEL = "WARNING"
else:
    config.LOG_LEVEL = "DEBUG"
