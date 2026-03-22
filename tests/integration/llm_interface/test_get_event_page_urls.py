import pytest
from pathlib import Path

# Assuming llm fixture is available from conftest.py

def test_antonesnightclub_page1_event_urls(llm):
    markdown = Path("tests/assets/markdown/antonesnightclub_page1.md").read_text()
    current_url = "https://antonesnightclub.com/"

    # Expected URLs to be carefully extracted from the markdown
    # Based on content of antonesnightclub_page1.md
    expected_urls = [
            "https://antonesnightclub.com/tm-event/antones-stage-at-still-austin-monica-valli-single-release/",
            "https://antonesnightclub.com/tm-event/sxsw-superhuman-ai/",
            "https://antonesnightclub.com/tm-event/sxsw-superhuman-ai-2/",
            "https://antonesnightclub.com/tm-event/sxsw-superhuman-ai-3/",
            "https://antonesnightclub.com/tm-event/sxsw-top-dawg-entertainment-showcase/",
            "https://antonesnightclub.com/tm-event/austin-blues-fest-antones-forever-sxsw-2026-day-party/",
            "https://antonesnightclub.com/tm-event/lafayette-sheaukaze-crawfish-boil/",
            "https://antonesnightclub.com/tm-event/soul-man-sam-78th-birthday-bash-w-cc-adcock-the-lafayette-marquis/",
            "https://antonesnightclub.com/tm-event/booker-t-jones/",
            "https://antonesnightclub.com/tm-event/blue-monday-soul-man-sam-w-cesar-crespo/",
            "https://antonesnightclub.com/tm-event/kxllswxtch-eyesore-tour-w-warlord-colossus-druidess/",
            "https://antonesnightclub.com/tm-event/fia-the-love-me-tour/",
            "https://antonesnightclub.com/tm-event/antones-stage-at-still-austin-paul-val-w-soul-man-sam/",
            "https://antonesnightclub.com/tm-event/jay-webb/",
            "https://antonesnightclub.com/tm-event/winyah/",
            "https://antonesnightclub.com/tm-event/anthropos-arts-spring-fling-with-shinyribs/",
            "https://antonesnightclub.com/tm-event/jonah-kagen/",
            "https://antonesnightclub.com/tm-event/paul-cauthen/",
            "https://antonesnightclub.com/tm-event/jake-andrews-nate-boff/",
            "https://antonesnightclub.com/tm-event/tribezas-birthday-bash-tiffany-w-the-mcgrath-project/",
    ]

    event_urls = llm.get_event_page_urls(markdown, current_url=current_url)

    assert isinstance(event_urls, list)
    assert len(event_urls) > 0
    assert set(event_urls) == set(expected_urls)
