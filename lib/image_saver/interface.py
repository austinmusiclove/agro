from abc import ABC, abstractmethod


class ImageSaverError(Exception):
    pass


class ImageSaverInterface(ABC):
    def __init__(self, config_loader=None):
        self._config_loader = config_loader
        self._config = self._load_config()

    def _load_config(self) -> dict:
        if self._config_loader:
            return self._config_loader.get_config("agro").get("image_saver", {})
        return {}

    @abstractmethod
    def save(self, image_bytes: bytes, name_hint: str = None) -> str:
        """
        Saves image bytes to storage.

        Args:
            image_bytes: The raw bytes of the image.
            name_hint: Optional hint for human-readable filename component.

        Returns:
            The full absolute path to the saved image.
        """
        pass
