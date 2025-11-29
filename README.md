TQuiz Solver

This repository implements the required HTTP endpoint for the TDS LLM Analysis project. The system receives a POST request containing a quiz URL, fetches the quiz page (including JavaScript-rendered content), extracts the task, solves it using a combination of scraping, analysis, and LLM reasoning, and submits the answer back to the quiz server. The solver continues following new URLs until the quiz ends.

Features

FastAPI server hosting a single POST endpoint.

Secret-based authentication for every request.

JavaScript rendering using Playwright (Chromium).

Static HTML fallback using httpx.

Multi-phase quiz solving: each quiz may return the next URL.

Parser automatically extracts submit URL and any embedded instructions.

LLM module handles cases requiring reasoning, transcription, data analysis, or reconstruction of answers.

Responses always remain under 1 MB.

Designed to complete within 3 minutes of receiving a task.

Fully deployed on Render with HTTPS support.
