from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from app.logic import solve_quiz

SECRET = "YOUR_SECRET"

app = FastAPI()

@app.post("/")
async def receive_task(request: Request):
    try:
        payload = await request.json()
    except:
        return JSONResponse({"error": "Invalid JSON"}, status_code=400)

    if payload.get("secret") != SECRET:
        return JSONResponse({"error": "Forbidden"}, status_code=403)

    # Acknowledge receipt
    # MUST return 200 immediately
    response = {"status": "received"}
    
    # Start solving asynchronously
    # (Or use background tasks)
    await solve_quiz(payload)

    return response
