from .interface import ImageSaverInterface
from .local_image_saver import LocalImageSaver
from .s3_image_saver import S3ImageSaver


class ImageSaverFactory:
    DEFAULT_IMPLEMENTATION = "local"

    def __init__(self, config_loader):
        self._config_loader = config_loader
        self._default_implementation = config_loader.get_config("agro").get("image_saver", {}).get("default", self.DEFAULT_IMPLEMENTATION)

    def create(self, implementation: str = None) -> ImageSaverInterface:
        if implementation is None:
            implementation = self._default_implementation

        if implementation == "local":
            return LocalImageSaver(self._config_loader)
        elif implementation == "s3":
            return S3ImageSaver(self._config_loader)
        else:
            raise ValueError(f"Unknown image_saver type requested: {implementation}")
