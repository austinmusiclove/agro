from abc import ABC, abstractmethod


class LlmInterface(ABC):
    @abstractmethod
    def get_next_page_url(self, markdown):
        pass
