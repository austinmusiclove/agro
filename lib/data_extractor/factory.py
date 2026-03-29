from .interface import DataExtractorInterface
from .gemini_data_extractor import GeminiDataExtractor
from .openai_data_extractor import OpenAiDataExtractor


class DataExtractorFactory:
    def __init__(self, config_loader):
        self._config_loader = config_loader
        self._default_implementation = config_loader.get_config("agro").get("data_extractor", {}).get("default", "openai")

    def create(self, implementation: str = None) -> DataExtractorInterface:
        if implementation is None:
            implementation = self._default_implementation

        if implementation == "openai":
            return OpenAiDataExtractor(self._config_loader)
        elif implementation == "gemini":
            return GeminiDataExtractor(self._config_loader)
        else:
            raise ValueError(f"Unknown data extractor type: {implementation}")
