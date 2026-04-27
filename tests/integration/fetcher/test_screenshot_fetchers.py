import pytest
from lib.fetcher.drission_page_fetcher import DrissionPageFetcher
from lib.fetcher.playwright_fetcher import PlaywrightFetcher

@pytest.fixture(params=[DrissionPageFetcher, PlaywrightFetcher])
def screenshot_fetcher(request):
    return request.param()

def test_fetch_returns_screenshot_when_flag_is_true(screenshot_fetcher):
    result = screenshot_fetcher.fetch("https://austinmusiclove.github.io/agro/antonesnightclub_page1.html", return_screenshot=True)
    
    assert isinstance(result, dict)
    assert "html" in result
    assert "screenshot" in result
    assert isinstance(result["html"], str)
    assert isinstance(result["screenshot"], bytes)
    assert len(result["html"]) > 0
    assert len(result["screenshot"]) > 0
    assert result["screenshot"][:4] == b'\x89PNG'
