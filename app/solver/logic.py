import httpx
import logging
from urllib.parse import urlparse

from app.solver.browser import fetch_html
from app.solver.parser import extract_question_and_payload

log = logging.getLogger("solver")


# ---- Solve one phase ----

async def solve_single_phase(email: str, secret: str, url: str):
    log.info(f"Solving phase at: {url}")

    # Fetch with fallback to JS if required
    html = await fetch_html(url)

    # Parse submit URL + secret
    info = extract_question_and_payload(html, url)
    log.info(f"Parser result: {info}")

    submit_url = info.get("submit_url")
    answer = info.get("secret")

    if not submit_url:
        log.error("Submit URL not found. HTML snippet:")
        log.error(info["raw_html_snippet"])
        raise Exception("Submit URL not found")

    # If no answer found, answer = secret provided by the user
    if not answer:
        answer = secret

    log.info(f"Submitting to {submit_url} with answer={answer}")

    # Make submission request
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            submit_url,
            json={
                "email": email,
                "secret": secret,
                "url": url,
                "answer": answer
            }
        )
        resp.raise_for_status()

    data = resp.json()

    next_url = data.get("url")
    if next_url:
        log.info(f"Next URL found -> {next_url}")
    else:
        log.warning("No next URL found — assuming final phase reached.")

    return data


# ---- Main loop ----

async def solve_quiz_chain(email: str, secret: str, start_url: str):
    current_url = start_url
    phase = 1

    while True:
        log.info(f"=== Phase {phase}: {current_url} ===")

        result = await solve_single_phase(email, secret, current_url)

        next_url = result.get("url")
        if not next_url:
            # Final phase
            return result

        current_url = next_url
        phase += 1
