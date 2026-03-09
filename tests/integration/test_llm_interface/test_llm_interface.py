import pytest
from lib.llm_interface.ollama import OllamaLlm


def test_prompt_llm_integration():
    llm = OllamaLlm()
    result = llm._prompt_llm("Say 'hello' in one word")
    assert isinstance(result, str)
    assert len(result) > 0
