# app/main.py (patch / add these bits)
import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from app.solver.logic import solve_quiz_chain

app = FastAPI()
EXPECTED_SECRET = os.getenv("EXPECTED_SECRET")  # set this on Render to your secret

class QuizRequest(BaseModel):
    email: str
    secret: str
    url: str

@app.post("/")
async def handle_quiz(req: QuizRequest):
    # JSON validation handled by Pydantic; now check secret
    if EXPECTED_SECRET and req.secret != EXPECTED_SECRET:
        # 403 for invalid secret
        raise HTTPException(status_code=403, detail="Invalid secret")
    result = await solve_quiz_chain(req.email, req.secret, req.url)
    return {"status": "done", "result": result}

# debug endpoint to inspect parser code currently deployed
@app.get("/debug-parser")
def debug_parser():
    import inspect
    from app.solver import parser
    return {"parser_source": inspect.getsource(parser.extract_question_and_payload)}

# debug endpoint to ensure server environment is correct
@app.get("/debug-env")
def debug_env():
    return {"EXPECTED_SECRET_set": bool(EXPECTED_SECRET)}
