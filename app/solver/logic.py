# app/solver/logic.py
import logging
import httpx
from .browser import fetch_html
from .parser import extract_question_and_payload

logger = logging.getLogger("solver")
logging.basicConfig(level=logging.INFO)


async def solve_single_phase(email: str, secret: str, url: str, phase: int) -> str | None:
    """
    Visit `url`, parse submit target and secret, submit JSON and return next_url if present.
    phase param kept for logging and future heuristics.
    """
    logger.info("Solving phase %s at: %s", phase, url)
    html = await fetch_html(url)
    info = extract_question_and_payload(html, url)

    logger.info("Parser result: %s", {
        "submit_url": info.get("submit_url"),
        "secret_found": bool(info.get("secret"))
    })

    submit_url = info.get("submit_url")
    if not submit_url:
        # Helpful debug: log snippet and raise
        snippet = info.get("raw_html_snippet", "")[:1200]
        logger.error("Submit URL not found. HTML snippet (truncated):\n%s", snippet)
        raise Exception("Submit URL not found — parser failed")

    # Determine answer: prefer secret scraped; if not, use provided secret
    answer_value = info.get("secret") or secret or ""

    payload = {
        "email": email,
        "secret": secret,
        "url": url,
        "answer": answer_value,
    }

    # Post payload
    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.post(submit_url, json=payload)
        try:
            resp.raise_for_status()
        except Exception as e:
            # log resp body for debugging
            logger.error("POST to %s failed: %s - body: %s", submit_url, e, resp.text)
            raise

        try:
            data = resp.json()
        except Exception:
            logger.warning("Response is not JSON, returning None. raw=%s", resp.text)
            return None

    # Next URL may exist in 'url' or 'next' or 'next_url'
    next_url = data.get("url") or data.get("next") or data.get("next_url")
    logger.info("POST response: correct=%s next=%s", data.get("correct"), next_url)
    return next_url


async def solve_quiz_chain(email: str, secret: str, start_url: str) -> dict:
    """
    Loop through the quiz chain until no next URL returned.
    Returns final page.
    """
    current = start_url
    phase = 1
    visited = set()

    while True:
        if current in visited:
            logger.warning("URL loop detected, stopping: %s", current)
            return {"final": current}
        visited.add(current)

        next_url = await solve_single_phase(email, secret, current, phase)
        if not next_url:
            return {"final": current}
        current = next_url
        phase += 1
