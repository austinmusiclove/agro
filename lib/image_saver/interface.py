from abc import ABC, abstractmethod
import os


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

    @staticmethod
    def _detect_extension(image_bytes: bytes) -> str:
        if len(image_bytes) >= 8:
            if image_bytes[:8] == b"\x89PNG\r\n\x1a\n":
                return "png"
            if image_bytes[:2] == b"\xff\xd8":
                return "jpg"
            if image_bytes[:6] in (b"GIF87a", b"GIF89a"):
                return "gif"
            if image_bytes[:4] == b"RIFF" and image_bytes[8:12] == b"WEBP":
                return "webp"
        return "bin"

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
