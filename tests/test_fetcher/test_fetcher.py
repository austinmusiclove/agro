import pytest
from urllib.error import HTTPError
from lib.fetcher.fetcher import Fetcher
from tests.mocks.mock_llm_interface import MockLlmInterface
from lib.llm_interface.ollama import OllamaLlm


@pytest.fixture
def fetcher():
    return Fetcher(MockLlmInterface())


def test_fetch_returns_string(fetcher):
    result = fetcher.fetch("https://hiremusicians.com")
    assert isinstance(result, str)


def test_fetch_returns_html_with_content(fetcher):
    result = fetcher.fetch("https://hiremusicians.com")
    assert len(result) > 0


def test_fetch_raises_404_for_invalid_page(fetcher):
    with pytest.raises(HTTPError) as exc_info:
        fetcher.fetch("https://hiremusicians.com/fake-page-12345")
    assert exc_info.value.code == 404


def test_fetch_returns_markdown_when_flag_is_true(fetcher):
    result = fetcher.fetch("https://hiremusicians.com", return_markdown=True)
    assert isinstance(result, str)
    assert len(result) > 0


def test_fetch_returns_markdown_without_html_tags(fetcher):
    result = fetcher.fetch("https://hiremusicians.com", return_markdown=True)
    assert "<html" not in result.lower()
    assert "<!doctype" not in result.lower()


# TODO: Implement with a proper URL that has pagination
# def test_fetch_all_pages_integration():
#     fetcher = Fetcher(OllamaLlm())
#     result = fetcher.fetch_all_pages("https://hiremusicians.com", max_pages=2)
#     assert isinstance(result, list)
#     assert len(result) >= 1
