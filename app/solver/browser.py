import httpx
import os

async def render_page(url: str) -> str:
    # In production: use plain HTTP GET
    if os.getenv("RENDER"):
        async with httpx.AsyncClient() as client:
            r = await client.get(url)
            r.raise_for_status()
            return r.text

    # Local debugging: real Playwright
    from playwright.async_api import async_playwright
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(url, wait_until="networkidle")
        html = await page.content()
        await browser.close()
        return html
