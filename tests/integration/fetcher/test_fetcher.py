import pytest
from urllib.error import HTTPError
from lib.fetcher.simple_fetcher import SimpleFetcher
from lib.fetcher.drission_page_fetcher import DrissionPageFetcher


@pytest.fixture(params=[SimpleFetcher, DrissionPageFetcher])
def fetcher(request):
    return request.param()


def test_fetch_returns_string(fetcher):
    result = fetcher.fetch("https://hiremusicians.com")
    assert isinstance(result, str)


def test_fetch_returns_html_with_content(fetcher):
    result = fetcher.fetch("https://hiremusicians.com")
    assert len(result) > 0


def test_fetch_returns_markdown_when_flag_is_true(fetcher):
    result = fetcher.fetch("https://hiremusicians.com", return_markdown=True)
    assert isinstance(result, str)
    assert len(result) > 0


def test_fetch_returns_markdown_without_html_tags(fetcher):
    result = fetcher.fetch("https://hiremusicians.com", return_markdown=True)
    assert "<html" not in result.lower()
    assert "<!doctype" not in result.lower()


def test_fetch_raises_404_for_invalid_page():
    fetcher = SimpleFetcher()
    with pytest.raises(HTTPError):
        fetcher.fetch("https://hiremusicians.com/fake-page-12345")


def test_fetch_returns_screenshot_when_flag_is_true():
    drission_fetcher = DrissionPageFetcher()
    result = drission_fetcher.fetch("https://hiremusicians.com", return_screenshot=True)
    assert isinstance(result, dict)
    assert "html" in result
    assert "screenshot" in result
    assert isinstance(result["html"], str)
    assert isinstance(result["screenshot"], bytes)
    assert len(result["html"]) > 0
    assert len(result["screenshot"]) > 0
    assert result["screenshot"][:4] == b'\x89PNG'
