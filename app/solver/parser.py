from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import re
import json

# Known canonical submit endpoint used by the quizzes
FALLBACK_SUBMIT = "https://tds-llm-analysis.s-anand.net/submit"

def _origin_from_url(url: str) -> str:
    p = urlparse(url)
    return f"{p.scheme}://{p.netloc}"

def _first_json_like_from_pre(pre_text: str):
    # Try to find a JSON object inside the <pre> text
    # This tolerates some whitespace/newlines and trailing text.
    m = re.search(r"(\{[\s\S]*?\})", pre_text)
    if not m:
        return None
    txt = m.group(1)
    try:
        return json.loads(txt)
    except Exception:
        # Try to fix simple trailing commas / quotes — best effort
        try:
            cleaned = re.sub(r",\s*}", "}", txt)
            cleaned = re.sub(r",\s*]", "]", cleaned)
            return json.loads(cleaned)
        except Exception:
            return None

def extract_question_and_payload(html: str, page_url: str):
    """
    Parse rendered HTML and return:
      - submit_url (absolute)
      - secret (if found)
      - raw_html_snippet (first N chars) for debugging
    """
    soup = BeautifulSoup(html or "", "html.parser")
    snippet = (html or "")[:3000]

    # 1) Try to find explicit <a href> or <form action>
    for tag in soup.find_all(["a", "form"]):
        href = (tag.get("href") or tag.get("action") or "").strip()
        if href and "submit" in href:
            submit_url = urljoin(page_url, href)
            return {
                "submit_url": submit_url,
                "secret": None,
                "raw_html_snippet": snippet,
            }

    # 2) Direct text search for "/submit" (maybe not inside a tag)
    if "/submit" in (html or ""):
        # Build origin from page_url if needed
        origin = _origin_from_url(page_url)
        submit_url = urljoin(origin, "/submit")
        return {
            "submit_url": submit_url,
            "secret": None,
            "raw_html_snippet": snippet,
        }

    # 3) If page includes a span.origin that is filled by JS with window.location.origin,
    #    we can reconstruct origin from page_url and use it.
    if soup.select_one("span.origin") or 'class="origin"' in (html or ""):
        origin = _origin_from_url(page_url)
        submit_url = urljoin(origin, "/submit")
        return {
            "submit_url": submit_url,
            "secret": None,
            "raw_html_snippet": snippet,
        }

    # 4) Look for patterns like "POST this JSON to <origin>/submit" or "POST this JSON to"
    m = re.search(r"POST\s+this\s+JSON\s+to\s+([^\s<]+)", html or "", flags=re.I)
    if m:
        maybe_origin = m.group(1).strip().strip("/")
        # if it already contains submit, use directly; else append /submit
        if "submit" in maybe_origin:
            submit_url = maybe_origin
        else:
            # If it's like <span class="origin"> it's not a literal origin — fall back to page_url origin
            if "<" in maybe_origin or "span" in maybe_origin:
                origin = _origin_from_url(page_url)
                submit_url = urljoin(origin, "/submit")
            else:
                # probably a hostname or full origin string
                if maybe_origin.startswith("http"):
                    submit_url = maybe_origin if "submit" in maybe_origin else urljoin(maybe_origin, "/submit")
                else:
                    origin = _origin_from_url(page_url)
                    submit_url = urljoin(origin, maybe_origin + ("/submit" if "submit" not in maybe_origin else ""))
        return {"submit_url": submit_url, "secret": None, "raw_html_snippet": snippet}

    # 5) Try to extract secret from <pre> JSON if present
    secret = None
    pre = soup.find("pre")
    if pre:
        # Attempt to find JSON inside the <pre>
        parsed = _first_json_like_from_pre(pre.get_text())
        if parsed and isinstance(parsed, dict):
            # common keys: "secret"
            if "secret" in parsed:
                secret = parsed["secret"]
            elif "code" in parsed:
                secret = parsed["code"]

    # 6) As a last resort, use known fallback endpoint
    return {
        "submit_url": FALLBACK_SUBMIT,
        "secret": secret,
        "raw_html_snippet": snippet,
    }
