import pytest
from pathlib import Path


def test_04center_calendar_nopaging(llm):
    markdown = Path("tests/assets/markdown/04center_calendar_nopaging.md").read_text()
    result = llm.get_next_page_url(markdown)
    assert result is None


def test_cactuscafe_events_lastpage(llm):
    markdown = Path("tests/assets/markdown/cactuscafe_events_lastpage.md").read_text()
    result = llm.get_next_page_url(markdown)
    assert result is None


def test_cactuscafe_events_page1(llm):
    markdown = Path("tests/assets/markdown/cactuscafe_events_page1.md").read_text()
    result = llm.get_next_page_url(markdown, current_url="https://universityunions.utexas.edu/events?location=40&type=All")
    assert result is not None
    assert result.startswith("http")


def test_cherrywoodcoffeehouse_events_loadmore(llm):
    markdown = Path("tests/assets/markdown/cherrywoodcoffeehouse_events_loadmore.md").read_text()
    result = llm.get_next_page_url(markdown)
    assert result is None


def test_emosaustin_shows_nopaging(llm):
    markdown = Path("tests/assets/markdown/emosaustin_shows_nopaging.md").read_text()
    result = llm.get_next_page_url(markdown)
    assert result is None


def test_kickbuttcoffee_events_slider_nopaging(llm):
    markdown = Path("tests/assets/markdown/kickbuttcoffee_events_slider_nopaging.md").read_text()
    result = llm.get_next_page_url(markdown)
    assert result is None


def test_rosetteatx_upcoming_events_nopaging(llm):
    markdown = Path("tests/assets/markdown/rosetteatx_upcoming_events_nopaging.md").read_text()
    result = llm.get_next_page_url(markdown)
    assert result is None


def test_theabgb_events_nopaging(llm):
    markdown = Path("tests/assets/markdown/theabgb_events_nopaging.md").read_text()
    result = llm.get_next_page_url(markdown)
    assert result is None


def test_thesaxonpub_events_loadmore(llm):
    markdown = Path("tests/assets/markdown/thesaxonpub_events_loadmore.md").read_text()
    result = llm.get_next_page_url(markdown)
    assert result is None
