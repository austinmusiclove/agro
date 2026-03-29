import os
import yaml
from lib.config.config_loader_interface import ConfigLoaderInterface


class YamlConfigLoader(ConfigLoaderInterface):
    _instance = None

    def __new__(cls, base_config_dir: str = "config"):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, base_config_dir: str = "config"):
        if self._initialized:
            return
        env = os.getenv("AGRO_ENV", "local")
        self._config_dir = os.path.join(base_config_dir, env)
        self._cache = {}
        self._initialized = True

    def get_config(self, config_name: str) -> dict:
        if config_name in self._cache:
            return self._cache[config_name]

        config_path = os.path.join(self._config_dir, f"{config_name}.yaml")
        
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Config file not found: {config_path}")

        with open(config_path, "r") as f:
            config = yaml.safe_load(f)

        self._cache[config_name] = config
        return config
