import os
import pytest
from lib.llm_interface.ollama import OllamaLlm
from lib.llm_interface.gemini import GeminiLlm


@pytest.fixture
def llm():
    llm_provider = os.getenv("AGRO_LLM_PROVIDER", "ollama").lower()
    if llm_provider == "gemini":
        return GeminiLlm()
    return OllamaLlm()
