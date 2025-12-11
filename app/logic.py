import asyncio
import time
from app.browser import get_rendered_html
from app.solver.parser import extract_question
from app.solver.data_ops import compute_answer
from app.utils.http import submit_answer

async def solve_quiz(task):
    start = time.time()
    email = task["email"]
    secret = task["secret"]
    url = task["url"]

    while True:
        if time.time() - start > 180:
            print("❌ Timeout > 3 minutes")
            break

        # 1. Load quiz page (JS-rendered)
        html = await get_rendered_html(url)

        # 2. Extract question instructions
        question = extract_question(html)

        # 3. Produce answer
        answer = await compute_answer(question)

        # 4. Submit to the given submit URL
        result = await submit_answer(email, secret, url, answer)

        print("Submitted:", result)

        if result.get("correct") is True and "url" in result:
            # Continue to next quiz
            url = result["url"]
            continue

        # If no next URL, stop
        break
