from DrissionPage import ChromiumPage
from .interface import FetcherInterface


class DrissionPageFetcher(FetcherInterface):
    def __init__(self):
        self._browser = None

    def _get_browser(self):
        if self._browser is None:
            self._browser = ChromiumPage()
        return self._browser

    def _close_browser(self):
        if self._browser:
            self._browser.quit()
            self._browser = None

    def fetch(self, url, return_markdown=False, return_screenshot=False):
        browser = self._get_browser()
        try:
            browser.get(url)
            browser.wait.doc_loaded()
            html = browser.html
            self._close_browser()

            if return_screenshot:
                screenshot_bytes = browser.get_screenshot(as_bytes=True)
                return {
                    "html": self._convert_html_to_markdown(html) if return_markdown else html,
                    "screenshot": screenshot_bytes
                }

            if return_markdown:
                return self._convert_html_to_markdown(html)
            return html
        except Exception:
            self._close_browser()
            raise
