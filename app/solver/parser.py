# app/solver/parser.py
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import re
import logging

logger = logging.getLogger("solver.parser")


def _origin_from_url(url: str) -> str:
    p = urlparse(url)
    return f"{p.scheme}://{p.netloc}"


def extract_question_and_payload(html: str, page_url: str) -> dict:
    """
    Returns dict with keys:
      - submit_url: absolute URL to post answers (or None)
      - secret: extracted secret string (or None)
      - raw_html_snippet: first N chars for debugging
    """
    soup = BeautifulSoup(html or "", "html.parser")
    origin = _origin_from_url(page_url)

    # 1) Try finding an <a href="/submit"> or absolute submit link
    submit_url = None
    a = soup.find("a", href=True)
    if a:
        # If there is an explicit anchor to /submit or /submit with origin
        for el in soup.find_all("a", href=True):
            href = el.get("href", "")
            if href.endswith("/submit") or "/submit" in href:
                submit_url = urljoin(page_url, href)
                break

    # 2) Fallback: look for textual "POST this JSON to" or "/submit" presence
    if not submit_url:
        if "/submit" in (html or ""):
            # attempt to reconstruct using origin
            submit_url = urljoin(origin + "/", "/submit")

    # 3) Extract secret by scanning any <pre> JSON or scripts containing JSON
    secret = None
    # Prefer <pre> blocks
    for pre in soup.find_all("pre"):
        txt = pre.get_text()
        # naive JSON-like secret extraction
        m = re.search(r'"secret"\s*:\s*"([^"]+)"', txt)
        if m:
            secret = m.group(1)
            break
        # fallback: lines like secret: "abc"
        m2 = re.search(r"secret\s*[:=]\s*\"?([^\n\",}]+)\"?", txt)
        if m2:
            secret = m2.group(1).strip()
            break

    # 4) Also check inline scripts for encoded content that includes "secret"
    if not secret:
        for script in soup.find_all("script"):
            s = script.string or ""
            if "secret" in s:
                m = re.search(r'"secret"\s*:\s*"([^"]+)"', s)
                if m:
                    secret = m.group(1)
                    break
                m2 = re.search(r"secret\s*[:=]\s*\"?([^\n\",;]+)\"?", s)
                if m2:
                    secret = m2.group(1).strip()
                    break

    # 5) Extra fallback: plain-text "secret" in HTML
    if not secret and html:
        m = re.search(r'secret["\']?\s*[:=]\s*["\']?([A-Za-z0-9 _\-+]+)["\']?', html)
        if m:
            secret = m.group(1).strip()

    return {
        "submit_url": submit_url,
        "secret": secret,
        "raw_html_snippet": (html or "")[:4000],
    }
