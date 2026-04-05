import os
import yaml
from copy import deepcopy


class YamlConfigLoader:
    def __init__(self, base_config_dir: str = "config", config_overrides: dict = None):
        env = os.getenv("AGRO_ENV", "local")
        self._config_dir = os.path.join(base_config_dir, env)
        self._cache = {}
        self._config_overrides = config_overrides or {}

    def get_config(self, config_name: str) -> dict:
        if config_name in self._cache:
            return self._cache[config_name]

        config_path = os.path.join(self._config_dir, f"{config_name}.yaml")
        
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Config file not found: {config_path}")

        with open(config_path, "r") as f:
            config = yaml.safe_load(f)

        config = self._merge_overrides(config)

        self._cache[config_name] = config
        return config

    def _merge_overrides(self, config: dict) -> dict:
        if not self._config_overrides:
            return config
        
        merged = deepcopy(config)
        
        def merge_dict(base: dict, overrides: dict):
            for key, value in overrides.items():
                if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                    merge_dict(base[key], value)
                else:
                    base[key] = value
        
        merge_dict(merged, self._config_overrides)
        return merged
