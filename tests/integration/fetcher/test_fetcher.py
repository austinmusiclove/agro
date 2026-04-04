import pytest
from lib.fetcher.simple_fetcher import SimpleFetcher
from lib.fetcher.drission_page_fetcher import DrissionPageFetcher
from lib.fetcher.interface import FetchError


@pytest.fixture(params=[SimpleFetcher, DrissionPageFetcher])
def fetcher(request):
    return request.param()


def test_fetch_returns_string(fetcher):
    result = fetcher.fetch("https://austinmusiclove.github.io/agro/antonesnightclub_page1.html")
    assert isinstance(result, str)


def test_fetch_returns_html_with_content(fetcher):
    result = fetcher.fetch("https://austinmusiclove.github.io/agro/antonesnightclub_page1.html")
    assert len(result) > 0


def test_fetch_returns_markdown_when_flag_is_true(fetcher):
    result = fetcher.fetch("https://austinmusiclove.github.io/agro/antonesnightclub_page1.html", return_markdown=True)
    assert isinstance(result, str)
    assert len(result) > 0


def test_fetch_returns_markdown_without_html_tags(fetcher):
    result = fetcher.fetch("https://austinmusiclove.github.io/agro/antonesnightclub_page1.html", return_markdown=True)
    assert "<html" not in result.lower()
    assert "<!doctype" not in result.lower()


def test_fetch_raises_404_for_invalid_page(fetcher):
    with pytest.raises(FetchError):
        fetcher.fetch("https://austinmusiclove.github.io/agro/fake-page")
