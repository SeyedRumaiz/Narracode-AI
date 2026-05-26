"""
AI Code Explainer & Debugger — LangChain-powered FastAPI backend.
"""

import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

from chains import build_code_analysis_chain

from executor import run_python_code
from visualizer import generate_flowchart, estimate_complexity
from memory import save_memory


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
    session_id: str = "default"


class AnalyseResponse(BaseModel):
    language: str = ""
    explanation: str = ""
    story: str = ""
    bugs: list = []
    fixed_code: str = ""
    improvements: list = []
    questions: list = []
    time_complexity: str = ""
    space_complexity: str = ""
    complexity_explanation: str = ""
    docstring: str = ""
    unit_tests: str = ""
    flowchart: str = ""
    complexity: dict = {}
    execution_output: dict = {}


@app.get("/")
async def root():
    return {"status": "online", "service": "AI Code Explainer & Debugger"}


@app.post("/analyse", response_model=AnalyseResponse)
async def analyse_code(request: AnalyseRequest):
    if not request.code.strip():
        raise HTTPException(status_code=400, detail="Code input cannot be empty.")

    ollama_model = os.getenv("OLLAMA_MODEL", "")
    deepseek_model = os.getenv("DEEPSEEK_MODEL", "")
    deepseek_key = os.getenv("DEEPSEEK_API_KEY", "")

    has_ollama = ollama_model and ollama_model.strip()
    has_deepseek = deepseek_key and deepseek_key.strip()

    model_name = None
    if has_ollama:
        provider = "ollama"
        api_key = "ollama"
        model_name = ollama_model
    elif has_deepseek:
        provider = "deepseek"
        api_key = deepseek_key
        model_name = deepseek_model
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

        execution_output = run_python_code(request.code)
        flowchart = generate_flowchart(request.code)
        complexity = estimate_complexity(request.code)

        save_memory(request.session_id, {
            "code": request.code,
            "result": result
        })

        return {
            **result,
            "execution_output": execution_output,
            "flowchart": flowchart,
            "complexity": complexity
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
