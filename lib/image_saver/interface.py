from abc import ABC, abstractmethod


class ImageSaverError(Exception):
    pass


class ImageSaverInterface(ABC):
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
