import os
import uuid
from pathlib import Path

from .interface import ImageSaverInterface, ImageSaverError


class LocalImageSaver(ImageSaverInterface):
    def __init__(self, config_loader):
        super().__init__(config_loader)
        self._images_dir = self._config.get("local", {}).get("images_dir", "./images")
        self._ensure_directory_exists()

    def _ensure_directory_exists(self) -> None:
        Path(self._images_dir).mkdir(parents=True, exist_ok=True)

    def save(self, image_bytes: bytes, name_hint: str = None) -> str:
        self._ensure_directory_exists()

        unique_id = uuid.uuid4().hex
        if name_hint:
            safe_hint = "".join(c if c.isalnum() or c in "-_" else "-" for c in name_hint)
            filename = f"{safe_hint}_{unique_id}"
        else:
            filename = unique_id

        extension = self._detect_extension(image_bytes)
        full_filename = f"{filename}.{extension}" if extension else filename
        filepath = os.path.join(self._images_dir, full_filename)

        try:
            with open(filepath, "wb") as f:
                f.write(image_bytes)
        except IOError as e:
            raise ImageSaverError(f"Failed to write image to {filepath}: {e}") from e

        return os.path.abspath(filepath)
