# app/solver/llm.py
import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


async def plan_solution(task: str) -> str:
    """
    Ask the LLM to generate a reasoning plan.
    """
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system",
             "content": "You create a short plan to solve puzzles. Keep it concise."},
            {"role": "user", "content": f"Make a step-by-step plan for:\n{task}"}
        ]
    )
    return resp.choices[0].message["content"]


async def solve_with_llm(task: str, plan: str = None, audio: bytes = None) -> str:
    """
    General-purpose solver.
    Supports:
      - text puzzles
      - JSON fixing
      - markdown
      - audio transcription
      - fallback for unknown puzzles
    """

    messages = []

    if plan:
        messages.append({"role": "system",
                         "content": f"Use this plan to solve the puzzle:\n{plan}"})
    else:
        messages.append({"role": "system",
                         "content": "Solve the puzzle correctly."})

    messages.append({"role": "user", "content": task})

    # AUDIO HANDLING
    if audio:
        audio_resp = client.audio.transcriptions.create(
            model="gpt-4o-mini-tts",
            file={"audio": audio}
        )
        return audio_resp.text.strip()

    # NORMAL TEXT SOLVER
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages
    )

    return resp.choices[0].message["content"].strip()
