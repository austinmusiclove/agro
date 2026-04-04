from lib.fetcher.drission_page_fetcher import DrissionPageFetcher


def test_fetch_returns_screenshot_when_flag_is_true():
    drission_fetcher = DrissionPageFetcher()
    result = drission_fetcher.fetch("https://austinmusiclove.github.io/agro/antonesnightclub_page1.html", return_screenshot=True)
    assert isinstance(result, dict)
    assert "html" in result
    assert "screenshot" in result
    assert isinstance(result["html"], str)
    assert isinstance(result["screenshot"], bytes)
    assert len(result["html"]) > 0
    assert len(result["screenshot"]) > 0
    assert result["screenshot"][:4] == b'\x89PNG'
