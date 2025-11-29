# app/solver/browser.py
import asyncio
from playwright.async_api import async_playwright

import httpx
import logging

logger = logging.getLogger("browser")

USE_JS = True  # flip this OFF if debugging without Playwright


async def render_page(url: str) -> str:
    if not USE_JS:
        logger.info("Fetching URL without JS: %s", url)
        async with httpx.AsyncClient() as client:
            r = await client.get(url)
            return r.text

    logger.info("Fetching URL WITH JS: %s", url)

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(args=["--no-sandbox"], headless=True)
        page = await browser.new_page()
        await page.goto(url, wait_until="networkidle")
        content = await page.content()
        await browser.close()
        return content
