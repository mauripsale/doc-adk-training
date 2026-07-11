import os
import yaml
from pathlib import Path

class Config:
    _instance = None
    _config = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
            cls._instance._load_config()
        return cls._instance

    def _load_config(self):
        env = os.getenv("APP_ENV", "dev")
        # Il file si trova in app/app_utils/config.py
        # Saliamo di due livelli per arrivare alla root del progetto
        config_path = Path(__file__).parent.parent.parent / "conf" / env / "config.yaml"
        
        if not config_path.exists():
            # Fallback a dev se non trovato
            config_path = Path(__file__).parent.parent.parent / "conf" / "dev" / "config.yaml"
            
        if config_path.exists():
            with open(config_path, "r") as f:
                self._config = yaml.safe_load(f)
        else:
            self._config = {}

    def get(self, key, default=None):
        keys = key.split(".")
        value = self._config
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default
        return value if value is not None else default

config = Config()
