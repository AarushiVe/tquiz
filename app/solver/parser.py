from bs4 import BeautifulSoup
from urllib.parse import urljoin

def extract_question_and_payload(html: str, page_url: str):
    soup = BeautifulSoup(html, "html.parser")
    base = page_url.split("/demo")[0]

    # Detect submit
    submit_el = soup.find("a", href="/submit")
    if submit_el:
        submit_url = base + "/submit"
    else:
        if "/submit" in html:
            submit_url = base + "/submit"
        else:
            submit_url = None

    # Secret extraction
    secret = None
    pre = soup.find("pre")
    if pre:
        txt = pre.text
        if "secret" in txt:
            after = txt.split("secret")[1]
            secret = after.split("\"")[1]

    return {
        "submit_url": submit_url,
        "secret": secret,
        "raw_html_snippet": html[:2000],
    }
