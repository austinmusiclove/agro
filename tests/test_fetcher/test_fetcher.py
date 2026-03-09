import pytest
from urllib.error import HTTPError
from lib.fetcher.fetcher import Fetcher


@pytest.fixture
def fetcher():
    return Fetcher()


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
