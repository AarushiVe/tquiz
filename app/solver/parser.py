from bs4 import BeautifulSoup
from urllib.parse import urljoin
import json
import re


def extract_question_and_payload(html: str, page_url: str):
    """
    Robust parser for all demo phases:
    - Finds submit URL reliably
    - Extracts secret/answer from <pre> JSON
    - Handles /demo, /demo-scrape, /demo-audio
    """

    soup = BeautifulSoup(html, "html.parser")

    # ---------------------------
    # 1. SUBMIT URL
    # ---------------------------
    submit_url = None

    # Case 1: explicit <a href="/submit">
    a = soup.find("a", href="/submit")
    if a:
        submit_url = urljoin(page_url, a["href"])

    # Case 2: any text mentioning submit
    if submit_url is None:
        if "/submit" in html:
            submit_url = urljoin(page_url, "/submit")

    # ---------------------------
    # 2. Extract <pre> JSON block
    # ---------------------------
    secret_value = None
    pre = soup.find("pre")

    if pre:
        raw = pre.get_text()
        raw = raw.strip()

        # Try strict JSON first
        try:
            data = json.loads(raw)
            # If secret exists and is a plain string
            if isinstance(data, dict) and "answer" in data:
                # On /demo, answer is literally "anything you want"
                secret_value = data["answer"]
            elif "secret" in data:
                secret_value = data["secret"]
        except Exception:
            # Not valid JSON — fallback to regex
            pass

        # Regex fallback for lines like: "answer": "something"
        if secret_value is None:
            m = re.search(r'"answer"\s*:\s*"([^"]+)"', raw)
            if m:
                secret_value = m.group(1)

        # Regex fallback for "secret"
        if secret_value is None:
            m2 = re.search(r'"secret"\s*:\s*"([^"]+)"', raw)
            if m2:
                secret_value = m2.group(1)

    # ---------------------------
    # 3. EXTRA LOGIC FOR SCRAPE PHASE
    # ---------------------------
    # On /demo-scrape, the page uses JS to inject plaintext secret.
    # When rendered via playwright, the final HTML contains the secret literally.
    if secret_value is None:
        # Look for obvious plain-text patterns
        m3 = re.search(r"the secret code you scraped[\"']?\s*[:=]?\s*([A-Za-z0-9_-]+)", html)
        if m3:
            secret_value = m3.group(1)

    # ---------------------------
    # 4. EXTRA FOR AUDIO PHASE
    #     You will later replace with your actual DSP logic.
    # ---------------------------
    if secret_value is None and "demo-audio" in page_url:
        # placeholder — solver will inject real value
        secret_value = "0"

    # Final fallback
    if secret_value is None:
        secret_value = ""

    return {
        "submit_url": submit_url,
        "secret": secret_value,
        "raw_html_snippet": html[:2000],
    }
