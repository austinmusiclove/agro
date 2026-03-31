import atexit
from DrissionPage import ChromiumPage, ChromiumOptions
from .interface import FetcherInterface


_browser_instance = None


def _get_shared_browser():
    global _browser_instance
    if _browser_instance is None:
        options = ChromiumOptions().headless(True).auto_port()
        _browser_instance = ChromiumPage(options)
    return _browser_instance


def _close_shared_browser():
    global _browser_instance
    if _browser_instance:
        _browser_instance.quit()
        _browser_instance = None


atexit.register(_close_shared_browser)


class DrissionPageFetcher(FetcherInterface):
    def __init__(self):
        pass

    def fetch(self, url, return_markdown=False, return_screenshot=False):
        browser = _get_shared_browser()
        browser.get(url)
        browser.wait.doc_loaded()
        html = browser.html

        if return_screenshot:
            screenshot_bytes = browser.get_screenshot(as_bytes=True)
            return {
                "html": self._convert_html_to_markdown(html) if return_markdown else html,
                "screenshot": screenshot_bytes
            }

        if return_markdown:
            return self._convert_html_to_markdown(html)
        return html
