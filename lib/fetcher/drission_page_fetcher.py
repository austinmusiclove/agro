import atexit
import io
import os
import time
from DrissionPage import ChromiumPage, ChromiumOptions
from DrissionPage.errors import PageDisconnectedError
from PIL import Image
from .interface import FetcherInterface, FetchError


_browser_instance = None


def _close_shared_browser():
    global _browser_instance
    if _browser_instance:
        _browser_instance.quit()
        _browser_instance = None


atexit.register(_close_shared_browser)


class DrissionPageFetcher(FetcherInterface):
    DEFAULT_MAX_SCREENSHOT_HEIGHT = 16000

    def __init__(self, config_loader=None):
        super().__init__(config_loader)
        drission_config = self._config.get("drission_page", {})
        self.max_screenshot_height = drission_config.get("max_screenshot_height", self.DEFAULT_MAX_SCREENSHOT_HEIGHT)
        self.browser_path = drission_config.get("browser_path")

    def _get_browser(self):
        global _browser_instance
        if _browser_instance is None:

            options = ChromiumOptions()

            # Crucial: Use /tmp for the user profile and crash dumps
            # Lambda only allows writing to /tmp

            if self.browser_path:
                options.set_browser_path(self.browser_path)
                user_data_dir = '/tmp/user_data'
                os.makedirs(user_data_dir, exist_ok=True)
                options.set_user_data_path(user_data_dir)
                options.set_argument('--headless=new')
                options.set_argument('--no-sandbox')
                options.set_argument('--disable-gpu')
                options.set_argument('--disable-dev-shm-usage')
                options.set_argument('--single-process')
                #options.set_argument('--user-data-dir=/tmp/user-data')
                options.set_argument('--disk-cache-dir=/tmp/disk-cache')
                options.set_argument('--remote-debugging-port=9222') # Explicitly set the port
            else:
                options = ChromiumOptions().auto_port()
                options.headless(True)

            try:
                print('create browser')
                _browser_instance = ChromiumPage(options)
            except Exception as err:
                print('error from chrome page')
                print(err)

            print('got browser')
        return _browser_instance

    def fetch(self, url, return_markdown=False, return_screenshot=False):
        try:
            print('get browser')
            browser = self._get_browser()
            print('listen')
            browser.listen.start(targets=True)
            print('get')
            browser.get(url)
            print('after get')
            browser.wait.doc_loaded()
            response = browser.listen.wait()
            status_code = response.response.status if response else None

            if status_code and status_code != 200:
                raise FetchError(url, status_code)

            html = browser.html
            markdown = self._convert_html_to_markdown(html) if return_markdown else None
            screenshot = self._capture_screenshot(browser) if return_screenshot else None

            return {
                "html": html,
                "markdown": markdown,
                "screenshot": screenshot
            }

        except PageDisconnectedError as e:
            raise FetchError(url, reason="Connection lost") from e
        except FetchError:
            raise
        except Exception as e:
            raise FetchError(url, reason=str(e)) from e

    def _capture_screenshot(self, browser):
        time.sleep(2)
        browser.scroll.to_bottom()
        time.sleep(2)
        browser.wait.doc_loaded()
        browser.scroll.to_top()
        time.sleep(1)

        page_height = browser.run_js('''
            return Math.max(
                document.body.scrollHeight,
                document.documentElement.scrollHeight,
                document.body.offsetHeight,
                document.documentElement.offsetHeight,
                document.body.clientHeight,
                document.documentElement.clientHeight
            );
        ''')
        viewport_height = browser.rect.viewport_size[1]

        if page_height <= self.max_screenshot_height:
            screenshot_bytes = browser.get_screenshot(as_bytes=True, full_page=True)
        else:
            self._hide_sticky_elements(browser)
            screenshot_bytes = self._capture_screenshot_chunked(browser, viewport_height, page_height)
            self._restore_sticky_elements(browser)

        return screenshot_bytes

    def _capture_screenshot_chunked(self, browser, viewport_height, page_height):
        viewport_width = browser.rect.viewport_size[0]

        chunks = []
        y_offset = 0

        while y_offset < page_height:
            browser.run_js(f'window.scrollTo(0, {y_offset});')
            time.sleep(0.3)

            chunk_bytes = browser.get_screenshot(as_bytes=True, full_page=False)
            chunk_image = Image.open(io.BytesIO(chunk_bytes))
            chunks.append(chunk_image)

            y_offset += viewport_height

        full_image = Image.new('RGB', (viewport_width, page_height))

        y_position = 0
        for chunk in chunks:
            if y_position + chunk.height > page_height:
                cropped = chunk.crop((0, 0, viewport_width, page_height - y_position))
                full_image.paste(cropped, (0, y_position))
            else:
                full_image.paste(chunk, (0, y_position))
            y_position += chunk.height

        output = io.BytesIO()
        full_image.save(output, format='PNG')
        return output.getvalue()

    def _hide_sticky_elements(self, browser):
        browser.run_js('''
            (function() {
                window._originalStickyPositions = [];
                const fixedElements = document.querySelectorAll('[style*="position: fixed"], [style*="position: sticky"], [class*="sticky"], [class*="fixed"], [id*="sticky"], [id*="fixed"]');
                const allElements = document.getElementsByTagName('*');

                for (let el of allElements) {
                    const style = window.getComputedStyle(el);
                    if (style.position === 'fixed' || style.position === 'sticky') {
                        el.style.position = 'absolute';
                        window._originalStickyPositions.push({el: el, originalPosition: style.position});
                    }
                }
            })();
        ''')

    def _restore_sticky_elements(self, browser):
        browser.run_js('''
            (function() {
                if (window._originalStickyPositions) {
                    for (let item of window._originalStickyPositions) {
                        item.el.style.removeProperty('position');
                    }
                    window._originalStickyPositions = null;
                }
            })();
        ''')
