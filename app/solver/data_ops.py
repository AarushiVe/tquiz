import pandas as pd
import requests
from pypdf import PdfReader

async def compute_answer(question):
    text = question["instruction"]

    if "sum" in text and "value" in text:
        pdf_url = extract_pdf_url(text)
        pdf_bytes = requests.get(pdf_url).content
        reader = PdfReader(IOBytes(pdf_bytes))
        table = extract_table_from_page(reader, page=2)
        return int(table["value"].sum())

    # fallback to LLM if needed
    return "UNKNOWN"
