import requests
import json

async def submit_answer(email, secret, quiz_url, answer):
    payload = {
        "email": email,
        "secret": secret,
        "url": quiz_url,
        "answer": answer,
    }
    r = requests.post(
        extract_submit_url(quiz_url),
        data=json.dumps(payload),
        headers={"Content-Type": "application/json"}
    )
    return r.json()
