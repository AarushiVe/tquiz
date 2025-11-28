# app/solver/browser.py
from playwright.async_api import async_playwright

async def render_page(url: str) -> str:
    """
    Render the page using Playwright and return final HTML.
    We explicitly wait for #result to be present and add a small extra delay.
    """
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(url, wait_until="domcontentloaded")
        # Wait for result div to be populated (demo pages put data there).
        try:
            await page.wait_for_selector("#result", timeout=5000)
        except Exception:
            # If #result not present within 5s, continue anyway (some pages differ)
            pass
        # Additional short wait to let JS populate innerHTML
        await page.wait_for_timeout(1500)
        html = await page.content()
        await browser.close()
        return html
