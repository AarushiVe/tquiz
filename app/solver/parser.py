from bs4 import BeautifulSoup
from urllib.parse import urljoin

def extract_question_and_payload(html: str, page_url: str):
    soup = BeautifulSoup(html, "html.parser")

    # ---- 1. Detect /submit ----
    submit_url = None

    # Look for literal /submit anywhere
    if "/submit" in html:
        submit_url = urljoin(page_url, "/submit")

    # ---- 2. Extract secret ----
    secret = None
    pre = soup.find("pre")
    if pre:
        txt = pre.text
        if "secret" in txt:
            try:
                secret = txt.split('"secret"')[1]
                secret = secret.split("\n")[0]
                secret = secret.replace(":", "").replace(",", "")
                secret = secret.strip().strip('"')
            except:
                secret = None

    return {
        "submit_url": submit_url,
        "secret": secret,
        "raw_html_snippet": html[:2000]
    }
