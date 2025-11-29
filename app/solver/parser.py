# app/solver/parser.py
from bs4 import BeautifulSoup
from urllib.parse import urljoin

def extract_question_and_payload(html: str, page_url: str):
    soup = BeautifulSoup(html, "html.parser")

    # submit URL handling
    submit_url = None

    # Explicit <a href="/submit">
    a = soup.find("a", href="/submit")
    if a:
        submit_url = urljoin(page_url, "/submit")

    # Fallback: raw HTML contains /submit (Phase 1)
    if not submit_url and "/submit" in html:
        submit_url = urljoin(page_url, "/submit")

    # Secret extraction
    secret = None
    pre = soup.find("pre")
    if pre:
        txt = pre.get_text()
        if '"secret"' in txt:
            try:
                secret = txt.split('"secret"')[1].split('"')[1]
            except:
                pass

    return {
        "submit_url": submit_url,
        "secret": secret,
        "raw_html_snippet": html[:2000],
    }
