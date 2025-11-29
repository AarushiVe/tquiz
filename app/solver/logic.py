import logging
import httpx
from bs4 import BeautifulSoup

from .browser import fetch_no_js, fetch_with_js
from .parser import extract_question_and_payload

logger = logging.getLogger("solver")


async def solve_single_phase(email: str, secret: str, url: str, phase: int):
    """
    Phase 1 = simple static HTML
    Phase 2+ = requires JS-rendered HTML
    """
    logger.info(f"Solving phase at: {url}")

    # ---- key fix: use JS in Phase >=2 ----
    if phase == 1:
        html = await fetch_no_js(url)
    else:
        html = await fetch_with_js(url)

    result = extract_question_and_payload(html, url)

    submit_url = result.get("submit_url")

    if not submit_url:
        logger.error("Submit URL not found. HTML snippet:\n" + result["raw_html_snippet"])
        raise Exception("Submit URL not found")

    # Find answer
    answer = result.get("secret") or secret

    payload = {
        "email": email,
        "secret": secret,
        "url": url,
        "answer": answer,
    }

    async with httpx.AsyncClient(timeout=20) as client:
        r = await client.post(submit_url, json=payload)
        r.raise_for_status()
        data = r.json()

    next_url = data.get("next")
    return next_url


async def solve_quiz_chain(email: str, secret: str, start_url: str):
    current_url = start_url
    phase = 1

    while True:
        next_url = await solve_single_phase(email, secret, current_url, phase)

        if not next_url:
            return {"final": current_url}

        current_url = next_url
        phase += 1
