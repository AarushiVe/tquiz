# app/solver/parser.py
from bs4 import BeautifulSoup


def extract_question_and_payload(html: str, page_url: str):
    soup = BeautifulSoup(html, "html.parser")

    # -------------------------------------------------------------
    # 1. DETECT SUBMIT URL (works for demo, project2, real exam)
    # -------------------------------------------------------------
    submit_url = None

    # Case 1: explicit link
    a = soup.find("a", href="/submit")
    if a:
        submit_url = "https://tds-llm-analysis.s-anand.net/submit"

    # Case 2: found anywhere inside raw HTML
    elif "/submit" in html:
        submit_url = "https://tds-llm-analysis.s-anand.net/submit"

    # -------------------------------------------------------------
    # 2. EXTRACT "secret" FROM PRE BLOCK IF PRESENT
    # -------------------------------------------------------------
    secret = None
    pre = soup.find("pre")
    if pre:
        txt = pre.get_text(strip=True)
        if "secret" in txt:
            # Example inside <pre>:
            # { "email": "...", "secret": "XYZ", "url": "...", ... }
            try:
                after = txt.split('"secret"')[1]
                secret = after.split('"')[1]   # first quoted string after "secret"
            except Exception:
                pass

    # -------------------------------------------------------------
    # 3. RETURN RESULT
    # -------------------------------------------------------------
    return {
        "submit_url": submit_url,
        "secret":         secret,
        "raw_html_snippet": html[:2000],  # for debugging
    }
