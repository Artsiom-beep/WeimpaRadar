from contextlib import contextmanager
from playwright.sync_api import sync_playwright


@contextmanager
def open_page(
    url: str,
    *,
    viewport_w: int = 1440,
    viewport_h: int = 900,
    timeout_ms: int = 60_000,
):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": viewport_w, "height": viewport_h}
        )
        page = context.new_page()
        page.set_default_timeout(timeout_ms)
        page.set_default_navigation_timeout(timeout_ms)

        page.goto(url, wait_until="domcontentloaded")
        try:
            page.wait_for_load_state("networkidle", timeout=10_000)
        except Exception:
            pass

        try:
            yield page
        finally:
            try:
                context.close()
            finally:
                browser.close()
