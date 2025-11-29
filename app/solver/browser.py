import httpx
from playwright.async_api import async_playwright

async def fetch_without_js(url: str) -> str:
    async with httpx.AsyncClient() as client:
        r = await client.get(url)
        r.raise_for_status()
        return r.text


async def fetch_with_js(url: str) -> str:
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            await page.goto(url, timeout=15000)
            content = await page.content()
            await browser.close()
            return content
    except Exception:
        return None


async def fetch_html(url: str) -> str:
    # 1. Try simple GET
    html = await fetch_without_js(url)

    # If page includes <script> that builds next content → try JS
    if (
        "atob(" in html
        or "document.querySelector" in html
        or "innerHTML" in html
        or "script>" in html
        or "URLSearchParams" in html
    ):
        rendered = await fetch_with_js(url)
        if rendered:
            return rendered

    return html
