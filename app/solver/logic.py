# app/solver/logic.py
import json
import logging
from urllib.parse import urljoin

import httpx

from .browser import render_page
from .parser import extract_question_and_payload

logger = logging.getLogger("solver")
logging.basicConfig(level=logging.INFO)


async def solve_single_phase(email: str, secret: str, page_url: str):
    """
    Render the page (JS-enabled), parse for submit URL & payload, post a demo answer.
    Returns the parsed JSON response from the submit endpoint.
    Raises Exception when submit URL cannot be determined.
    """
    logger.info("Solving phase at: %s", page_url)

    # 1) Render page (JS-enabled)
    html = await render_page(page_url)

    # 2) Parse the rendered HTML using parser
    info = extract_question_and_payload(html, page_url) or {}
    logger.info("Parser result: %s", json.dumps(info, indent=2))

    submit_url = info.get("submit_url")

    # 3) Fallbacks if parser didn't find submit_url
    if not submit_url:
        # If the literal "/submit" appears somewhere, assume root submit path on same origin
        if "/submit" in html:
            submit_url = urljoin(page_url, "/submit")
            logger.warning("Parser didn't return submit_url; using urljoin fallback -> %s", submit_url)

    if not submit_url:
        # last-resort: scan for absolute "https://.../submit" in raw HTML
        try:
            import re

            m = re.search(r"(https?://[^\s'\"<>]+?/submit)", html)
            if m:
                submit_url = m.group(1)
                logger.warning("Found absolute submit URL by regex: %s", submit_url)
        except Exception:
            pass

    # 4) If still none, log snippet and raise for easier debugging on Render
    if not submit_url:
        snippet = info.get("raw_html_snippet", html[:2000])
        logger.error("Submit URL not found. HTML snippet (truncated):\n%s", snippet)
        raise Exception("Submit URL not found")

    # 5) Build payload (demo/simple). You can replace this with real solution later.
    # Prefer using parser-provided answer/secret when present.
    answer_value = info.get("example_answer", info.get("secret")) or "dummy"
    payload = {
        "email": email,
        "secret": secret,
        "url": page_url,
        "answer": answer_value,
    }

    # 6) Post the answer to submit_url
    logger.info("Submitting to %s with answer=%s", submit_url, str(payload.get("answer")))
    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.post(submit_url, json=payload)
        resp.raise_for_status()
        try:
            return resp.json()
        except ValueError:
            # non-json reply
            return {"raw_text": (await resp.aread()).decode(errors="replace")}


async def solve_quiz_chain(email: str, secret: str, start_url: str = None, **kwargs):
    """
    Drive the multi-phase quiz chain starting at start_url (or positional fallback).
    Returns the final response dict from the service.
    """
    # Accept either start_url kw or positional fallback (positional calls may pass third arg)
    if start_url is None:
        # sometimes callers pass url as 'url' key; accept that too
        start_url = kwargs.get("url")
    if not start_url:
        raise ValueError("start_url (or url) must be provided")

    current_url = start_url
    last_result = None

    # Safety: don't loop forever
    for phase_num in range(1, 25):
        logger.info("=== Phase %d: %s ===", phase_num, current_url)
        try:
            result = await solve_single_phase(email, secret, current_url)
        except Exception as e:
            logger.exception("Phase %d failed: %s", phase_num, e)
            raise

        last_result = result

        # Try common fields for next URL
        next_url = None
        if isinstance(result, dict):
            # common shapes: {"url": "..."} or {"next_url": "..."} or {"next": "..."}
            next_url = result.get("url") or result.get("next_url") or result.get("next")

            # Some services may return nested { "result": { "url": "..." } }
            if not next_url:
                nested = result.get("result") if isinstance(result.get("result"), dict) else None
                if nested:
                    next_url = nested.get("url") or nested.get("next_url") or nested.get("next")

        # If next_url is present and looks like a relative/absolute path, normalize it
        if next_url:
            # If next_url is relative like "/demo-scrape?...", make absolute using current_url as base
            next_url = urljoin(current_url, next_url)
            logger.info("Next URL found -> %s", next_url)
            current_url = next_url
            continue
        else:
            # No next URL -> assume final phase reached
            logger.warning("No next URL found — assuming final phase reached.")
            break

    return last_result
