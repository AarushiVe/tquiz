# app/solver/parser.py
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin

def extract_question_and_payload(html: str, page_url: str):
    soup = BeautifulSoup(html, "html.parser")

    # Detect base origin like: https://tds-llm-analysis.s-anand.net
    parsed = urlparse(page_url)
    origin = f"{parsed.scheme}://{parsed.netloc}"

    submit_url = None

    # Case 1: explicit <a href="/submit">
    el = soup.find("a", href="/submit")
    if el:
        submit_url = origin + "/submit"

    # Case 2: detect '/submit' text anywhere in HTML
    if not submit_url and "/submit" in html:
        submit_url = origin + "/submit"

    # Case 3: project2 pages always use origin/submit
    if not submit_url and "project2" in page_url:
        submit_url = origin + "/submit"

    # Extract secret if present (demo pages only)
    secret = None
    pre = soup.find("pre")
    if pre and "secret" in pre.text:
        try:
            after = pre.text.split("secret")[1]
            secret = after.split('"')[1]
        except:
            pass

    return {
        "submit_url": submit_url,
        "secret": secret,
        "raw_html_snippet": html[:2000],
    }
