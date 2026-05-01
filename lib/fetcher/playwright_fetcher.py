import atexit
from playwright.sync_api import sync_playwright, Error as PlaywrightError
from .interface import FetcherInterface, FetchError

_playwright_context = None
_browser_instance = None
_shared_context = None


def _close_shared_browser():
    global _playwright_context, _browser_instance, _shared_context
    if _shared_context:
        try:
            _shared_context.close()
        except:
            pass
        _shared_context = None
    if _browser_instance:
        try:
            _browser_instance.close()
        except:
            pass
        _browser_instance = None
    if _playwright_context:
        try:
            _playwright_context.stop()
        except:
            pass
        _playwright_context = None


atexit.register(_close_shared_browser)


class PlaywrightFetcher(FetcherInterface):
    def __init__(self, config_loader=None):
        super().__init__(config_loader)
        playwright_config = self._config.get("playwright", {})
        self.browser_path = playwright_config.get("browser_path")

    def _get_configured_browser(self):
        global _playwright_context, _browser_instance, _shared_context

        # If the browser or context exists but disconnected, force a restart
        if _browser_instance is not None and (not _browser_instance.is_connected() or _shared_context is None):
            _close_shared_browser()

        if _playwright_context is None:
            _playwright_context = sync_playwright().start()

            launch_args = {
                "headless": True,
                "args": [
                    "--single-process",        # Essential: keeps everything in one process
                    "--no-sandbox",           # Disables the security sandbox (required for root/Docker)
                    "--disable-dev-shm-usage", # Forces Chrome to use /tmp instead of shared memory
                    "--disable-gpu",           # No hardware acceleration in Lambda
                    "--disable-setuid-sandbox",
                    "--no-zygote",             # Prevents background "helper" processes
                    "--ignore-certificate-errors",
                ]
            }
            if self.browser_path:
                launch_args["executable_path"] = self.browser_path

            _browser_instance = _playwright_context.chromium.launch(**launch_args)
            _shared_context = _browser_instance.new_context(
                viewport={'width': 1280, 'height': 800}
            )

        return _browser_instance

    def fetch(self, url, return_markdown=False, return_screenshot=False):
        browser = self._get_configured_browser()
        page = _shared_context.new_page()

        try:
            response = page.goto(url, wait_until='networkidle', timeout=30000)

            if response and not response.ok:
                raise FetchError(url, response.status, response.status_text)

            # Handle lazy loading by scrolling
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            page.wait_for_timeout(2000)
            page.evaluate("window.scrollTo(0, 0)")
            page.wait_for_timeout(1000)

            html = page.content()
            markdown = self._convert_html_to_markdown(html) if return_markdown else None

            screenshot = None
            if return_screenshot:
                # Playwright handles full page screenshots natively
                screenshot = page.screenshot(full_page=True, type='png')

            return {
                "html": html,
                "markdown": markdown,
                "screenshot": screenshot
            }

        except PlaywrightError as e:
            if "closed" in str(e).lower() or "crashed" in str(e).lower():
                _close_shared_browser()
            raise FetchError(url, reason=str(e)) from e
        except FetchError:
            raise
        except Exception as e:
            raise FetchError(url, reason=str(e)) from e
        finally:
            if page:
                page.close()
