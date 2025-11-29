# app/solver/browser.py
import httpx
from playwright.async_api import async_playwright

# ----------------------------------------
# Renamed for compatibility with logic.py
# ----------------------------------------
async def fetch_no_js(url: str) -> str:
    async with httpx.AsyncClient() as client:
        r = await client.get(url)
        r.raise_for_status()
        return r.text


async def fetch_with_js(url: str) -> str:
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            await page.goto(url, timeout=20000, wait_until="networkidle")
            html = await page.content()
            await browser.close()
            return html
    except Exception as e:
        print("JS fetch failed:", e)
        return None


async def fetch_html(url: str) -> str:
    """Try static first, fallback to JS if script-like content is detected."""
    html = await fetch_no_js(url)

    if any(k in html for k in ["atob(", "URLSearchParams", "innerHTML", "<script"]):
        js = await fetch_with_js(url)
        if js:
            return js

    return html
