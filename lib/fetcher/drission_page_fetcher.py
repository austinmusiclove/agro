import atexit
import time
from DrissionPage import ChromiumPage, ChromiumOptions
from DrissionPage.errors import PageDisconnectedError
from .interface import FetcherInterface, FetchError


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
        try:
            browser = _get_shared_browser()
            browser.listen.start(targets=True)
            browser.get(url)
            browser.wait.doc_loaded()
            response = browser.listen.wait()
            status_code = response.response.status if response else None

            if status_code and status_code != 200:
                raise FetchError(url, status_code)

            html = browser.html

            if return_screenshot:
                browser.wait.doc_loaded()
                time.sleep(2)
                browser.scroll.to_bottom()
                time.sleep(2)
                browser.wait.doc_loaded()
                browser.scroll.to_top()
                time.sleep(1)
                screenshot_bytes = browser.get_screenshot(as_bytes=True, full_page=True)
                return {
                    "html": self._convert_html_to_markdown(html) if return_markdown else html,
                    "screenshot": screenshot_bytes
                }

            if return_markdown:
                return self._convert_html_to_markdown(html)
            return html
        except PageDisconnectedError as e:
            raise FetchError(url, reason="Connection lost") from e
        except FetchError:
            raise
        except Exception as e:
            raise FetchError(url, reason=str(e)) from e
