# app/solver/logic.py

import httpx
import logging
import json
from .browser import render_page
from .parser import extract_question_and_payload

logger = logging.getLogger("solver")


async def solve_single_phase(email: str, secret: str, url: str):
    """Solve one page and return server response."""
    logger.info(f"Solving phase at: {url}")

    # Render page with JS enabled
    html = await render_page(url)

    # Parse
    info = extract_question_and_payload(html, url)

    logger.info("Parser result: %s", json.dumps(info, indent=2))

    submit_url = info["submit_url"]
    if not submit_url:
        raise Exception("Submit URL not found")

    answer = info["secret"]  # Parsed secret/answer

    logger.info(f"Submitting to {submit_url} with answer={answer}")

    payload = {
        "email": email,
        "secret": secret,
        "url": url,
        "answer": answer,
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.post(submit_url, json=payload)
        resp.raise_for_status()
        return resp.json()


async def solve_quiz_chain(email: str, secret: str, url: str):
    """Follow chain: demo → scrape → audio → ... until no more phases"""
    current_url = url

    while True:
        result = await solve_single_phase(email, secret, current_url)

        # server returns {"correct":true,"url":next_url,...}
        next_url = result.get("url")

        if not next_url:
            logger.warning("No next URL found — assuming final phase reached.")
            return result

        # Continue to next phase
        current_url = next_url
