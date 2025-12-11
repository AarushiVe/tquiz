import re
from bs4 import BeautifulSoup

def extract_question(html):
    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text("\n")
    
    # naive parser — works for the sample structure
    submit_url = re.search(r'https?://\S+submit\S*', text)
    question = {
        "instruction": text,
        "submit_url": submit_url.group(0) if submit_url else None
    }
    return question
