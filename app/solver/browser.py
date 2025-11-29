# app/solver/browser.py
import httpx
from playwright.async_api import async_playwright
import logging

logger = logging.getLogger("solver.browser")


async def fetch_without_js(url: str, timeout: float = 15.0) -> str:
    async with httpx.AsyncClient(timeout=timeout) as client:
        r = await client.get(url)
        r.raise_for_status()
        return r.text


async def fetch_with_js(url: str, timeout: float = 15_000) -> str | None:
    """
    Use Playwright to render page if necessary.
    Returns None on failure (so caller can fall back).
    """
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            await page.goto(url, timeout=timeout)
            content = await page.content()
            await browser.close()
            return content
    except Exception as e:
        logger.warning("JS render failed for %s: %s", url, e)
        return None


async def fetch_html(url: str) -> str:
    """
    Attempt to fetch without JS first. If the result looks like it requires JS
    (atob, inline script building DOM, URLSearchParams etc.) retry with Playwright.
    """
    html = await fetch_without_js(url)
    hint_tokens = ("atob(", "URLSearchParams", "document.querySelector", "innerHTML", "<script")
    if any(tok in html for tok in hint_tokens):
        rendered = await fetch_with_js(url)
        if rendered:
            return rendered
    return html
