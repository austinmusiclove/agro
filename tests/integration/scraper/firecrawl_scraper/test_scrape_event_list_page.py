import threading
import http.server
import socketserver
from pathlib import Path
import pytest
from dotenv import load_dotenv

from lib.scraper.firecrawl_scraper import FirecrawlScraper

@pytest.fixture(scope="module")
def local_server():
    """Starts a local HTTP server serving the tests/assets/html directory."""
    # Ensure env vars are loaded (specifically for FIRECRAWL_API_URL if needed)
    load_dotenv(override=True)

    # tests/integration/scraper/firecrawl_scraper/test_... -> tests/assets/html
    html_dir = Path(__file__).parent.parent.parent.parent / "assets" / "html"

    class Handler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=str(html_dir), **kwargs)

        # Suppress log messages for cleaner test output
        def log_message(self, format, *args):
            pass

    # Find an open port
    httpd = socketserver.TCPServer(("", 0), Handler)
    port = httpd.server_address[1]

    # Run the server in a separate daemon thread
    server_thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    server_thread.start()

    # Yield the base URL to the test
    yield f"http://localhost:{port}"

    # Cleanup after tests
    httpd.shutdown()
    httpd.server_close()
    server_thread.join(timeout=1)

@pytest.mark.integration
def test_scrape_event_list_page_from_local_html(local_server):
    scraper = FirecrawlScraper()
    test_url = f"{local_server}/antonesnightclub_page1.html"

    # Act: Scrape the local URL (disable pagination for a single file test)
    events = scraper.scrape_event_list_page(test_url, paginate=False)
    print(events)

    # Assert
    assert events is not None, "Events list should not be None"
    assert isinstance(events, list), "Events should be a list"
    assert len(events) > 0, "No events were found in the HTML asset."

    # Validate the first event matches our schema structure
    first_event = events[0]
    assert "title" in first_event, "Event is missing a title"
    assert "event_page_url" in first_event, "Event is missing event_page_url"
    assert first_event["title"], "Event title should not be empty"
