import pytest
from dotenv import load_dotenv

from lib.scraper.firecrawl_scraper import FirecrawlScraper

@pytest.mark.integration
def test_scrape_event_list_page_from_local_html():
    load_dotenv(override=True)

    scraper = FirecrawlScraper()
    # This URL points to the test asset we deployed to the gh-pages branch
    test_url = "https://austinmusiclove.github.io/agro/antonesnightclub_page1.html"

    # Act: Scrape the GitHub Pages URL (disable pagination for a single file test)
    events = scraper.scrape_event_list_page(test_url, paginate=False)

    # Assert
    assert events is not None, "Events list should not be None"
    assert isinstance(events, list), "Events should be a list"
    assert len(events) > 0, "No events were found."
    assert len(events) == 20, f"Events were found but not exactly 20, got {len(events)}."

    # Validate the first event data
    first_event = events[0]
    correct_first_event = {
        'title': "Antone's Stage at Still Austin: Monica Valli (Single Release)",
        'start_date': '2026-03-13',
        'end_date': None,
        'start_time': '8:00pm',
        'end_time': None,
        'image': 'https://antonesnightclub.com/wp-content/uploads/2026/02/BarbaraFG_MonicaValli_Feb2026_2048x1152.jpg',
        'venue_name': "Antone's Stage at Still Austin",
        'performer_names': ['Monica Valli'],
        'indoor_outdoor': 'outdoor',
        'ages': 'All Ages',
        'price': 'Free',
        'event_list_page_url': 'https://www.stillaustin.com/antones-stage',
        'event_page_url': 'https://antonesnightclub.com/tm-event/antones-stage-at-still-austin-monica-valli-single-release/'
    }
    print(first_event)

    # Field-by-field assertions
    assert first_event["title"] == correct_first_event["title"], "Event title is incorrect"
    assert first_event["start_date"] == correct_first_event["start_date"], "start_date is incorrect"
    assert first_event["end_date"] == correct_first_event["end_date"], "end_date is incorrect"
    assert first_event["start_time"] == correct_first_event["start_time"], "start_time is incorrect"
    assert first_event["end_time"] == correct_first_event["end_time"], "end_time is incorrect"
    assert first_event["image"] == correct_first_event["image"], "image is incorrect"
    assert first_event["venue_name"] == correct_first_event["venue_name"], "venue_name is incorrect"
    assert first_event["performer_names"] == correct_first_event["performer_names"], "performer_names is incorrect"
    assert first_event["indoor_outdoor"] == correct_first_event["indoor_outdoor"], "indoor_outdoor is incorrect"
    assert first_event["ages"] == correct_first_event["ages"], "ages is incorrect"
    assert first_event["price"] == correct_first_event["price"], "price is incorrect"
    assert first_event["event_list_page_url"] == correct_first_event["event_list_page_url"], "event_list_page_url is incorrect"
    assert first_event["event_page_url"] == correct_first_event["event_page_url"], "event_page_url is incorrect"

@pytest.mark.integration
def test_scrape_event_list_page_pagination():
    load_dotenv(override=True)
    scraper = FirecrawlScraper()
    test_url = "https://austinmusiclove.github.io/agro/antonesnightclub_page1.html"
    # Act: Scrape with pagination enabled
    events = scraper.scrape_event_list_page(test_url, paginate=True)
    print('total events: ')
    print(len(events))
    # Assert
    assert events is not None, "Events list should not be None"
    assert isinstance(events, list), "Events should be a list"
    assert len(events) > 0, "No events were found."
    assert len(events) == 68, f"Expected 68 events across all pages, got {len(events)}"
