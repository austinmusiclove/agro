import pytest


def test_prompt_llm_integration(llm):
    result = llm._prompt_llm("Say 'hello' in one word")
    assert isinstance(result, str)
    assert len(result) > 0
