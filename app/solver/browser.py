import httpx
import logging

logger = logging.getLogger("browser")


async def render_page(url: str) -> str:
    """
    On Render, Playwright is unavailable. So we always fall back
    to simple HTTP GET. This still works for all phases because
    the server returns enough HTML without JS.
    """
    try:
        # Simple GET
        logger.info(f"Fetching URL without JS: {url}")
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            return resp.text

    except Exception as e:
        logger.error(f"Fallback fetch failed: {e}")
        raise
