# app/main.py
from fastapi import FastAPI
from pydantic import BaseModel
from app.solver.logic import solve_quiz_chain

class QuizRequest(BaseModel):
    email: str
    secret: str
    url: str

app = FastAPI()

@app.post("/")
async def handle_quiz(req: QuizRequest):
    result = await solve_quiz_chain(
        email=req.email,
        secret=req.secret,
        start_url=req.url
)

    return {"status": "done", "result": result}
