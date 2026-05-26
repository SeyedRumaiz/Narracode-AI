"""
AI Code Explainer & Debugger — LangChain-powered FastAPI backend.
"""

import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

from chains import build_code_analysis_chain

load_dotenv()

app = FastAPI(
    title="AI Code Explainer & Debugger",
    description="Analyse, debug, and improve code using LangChain + GPT",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class AnalyseRequest(BaseModel):
    code: str
    language: str = "auto-detect"


class AnalyseResponse(BaseModel):
    language: str = "python"
    explanation: str = ""
    story: str = ""
    bugs: list[dict] = []
    fixed_code: str = ""
    improvements: list[str] = []
    questions: list[dict] = []
    time_complexity: str = "O(1)"
    space_complexity: str = "O(1)"
    complexity_explanation: str = ""
    docstring: str = ""
    unit_tests: str = ""


@app.get("/")
async def root():
    return {"status": "online", "service": "AI Code Explainer & Debugger"}


@app.post("/analyse", response_model=AnalyseResponse)
async def analyse_code(request: AnalyseRequest):
    if not request.code.strip():
        raise HTTPException(status_code=400, detail="Code input cannot be empty.")

    openai_key = os.getenv("OPENAI_API_KEY", "")
    gemini_key = os.getenv("GEMINI_API_KEY", "")
    ollama_model = os.getenv("OLLAMA_MODEL", "")

    has_openai = openai_key and openai_key.strip() and openai_key != "your_openai_api_key_here"
    has_gemini = gemini_key and gemini_key.strip() and gemini_key != "your_gemini_api_key_here"
    has_ollama = ollama_model and ollama_model.strip() and ollama_model != "your_ollama_model_here"

    model_name = None
    if has_ollama:
        provider = "ollama"
        api_key = "ollama"
        model_name = ollama_model
    elif has_gemini:
        provider = "google"
        api_key = gemini_key
    elif has_openai:
        provider = "openai"
        api_key = openai_key
    else:
        raise HTTPException(
            status_code=503,
            detail="No LLM providers configured. Please set OLLAMA_MODEL, GEMINI_API_KEY, or OPENAI_API_KEY in backend/.env",
        )

    try:
        # Determine number of Q&A questions dynamically based on code line count
        line_count = len(request.code.strip().splitlines())
        if line_count <= 10:
            num_questions = 5
        elif line_count <= 20:
            num_questions = 7
        else:
            num_questions = 10

        chain = build_code_analysis_chain(api_key, provider=provider, model_name=model_name)
        result = chain.invoke({
            "code": request.code,
            "language": request.language,
            "num_questions": num_questions
        })
        return result
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
