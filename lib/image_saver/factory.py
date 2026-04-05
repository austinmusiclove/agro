from .interface import ImageSaverInterface
from .local_image_saver import LocalImageSaver


class ImageSaverFactory:
    def __init__(self, config_loader, config_overrides: dict = None):
        self._config_loader = config_loader
        self._config_overrides = config_overrides or {}
        self._default_implementation = config_loader.get_config("agro").get("image_saver", {}).get("default", "local")

    def create(self, implementation: str = None) -> ImageSaverInterface:
        if implementation is None:
            implementation = self._default_implementation

        if implementation == "local":
            return LocalImageSaver(self._config_loader, self._config_overrides)
        else:
            raise ValueError(f"Unknown image_saver type requested: {implementation}")
