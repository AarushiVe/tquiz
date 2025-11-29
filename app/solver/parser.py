from bs4 import BeautifulSoup
from urllib.parse import urljoin

def extract_question_and_payload(html: str, page_url: str):
    soup = BeautifulSoup(html, "html.parser")

    # The quiz ALWAYS submits to this HQ endpoint, not relative links.
    SUBMIT_BASE = "https://tds-llm-analysis.s-anand.net/submit"

    # Try to detect any "submit" link in page first
    submit_url = None

    # Case 1: Look for any <a>, <form>, or href containing "submit"
    for tag in soup.find_all(["a", "form"]):
        href = tag.get("href") or tag.get("action")
        if href and "submit" in href:
            submit_url = urljoin(page_url, href)
            break

    # Case 2: If still not found → Use global submit endpoint
    if not submit_url:
        submit_url = SUBMIT_BASE

    # Extract secret if present
    secret = None
    pre = soup.find("pre")
    if pre:
        txt = pre.text
        if "secret" in txt:
            try:
                after = txt.split("secret")[1]
                secret = after.split("\"")[1]
            except:
                pass

    return {
        "submit_url": submit_url,
        "secret": secret,
        "raw_html_snippet": html[:2000],
    }
