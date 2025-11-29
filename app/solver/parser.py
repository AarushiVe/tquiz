from bs4 import BeautifulSoup
from urllib.parse import urljoin

def extract_question_and_payload(html: str, page_url: str):
    soup = BeautifulSoup(html, "html.parser")

    # page origin, like https://tds-llm-analysis.s-anand.net
    origin = page_url.split("/project2")[0].split("/demo")[0]

    # Try to detect submit automatically
    submit_url = None

    # Case 1: explicit <a href="/submit">
    el = soup.find("a", href="/submit")
    if el:
        submit_url = origin + "/submit"

    # Case 2: detect "/submit" anywhere in HTML
    if not submit_url and "/submit" in html:
        submit_url = origin + "/submit"

    # Case 3: project2 pages → always use origin/submit
    if not submit_url:
        submit_url = origin + "/submit"

    # Extract secret if shown (demo only)
    secret = None
    pre = soup.find("pre")
    if pre and "secret" in pre.text:
        try:
            after = pre.text.split("secret")[1]
            secret = after.split('"')[1]
        except Exception:
            pass

    return {
        "submit_url": submit_url,
        "secret": secret,
        "raw_html_snippet": html[:2000]
    }
