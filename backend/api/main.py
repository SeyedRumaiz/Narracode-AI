"""AI Code Explainer & Debugger — LangChain-powered FastAPI backend."""

import json
import os
from typing import Any, Dict, List

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from backend.api.schemas import (
    AnalyseRequest,
    AnalyseResponse,
    AnalysisJobRequest,
    AnalysisJobResponse,
    AnalysisJobStatus,
)
from backend.chains import build_code_analysis_chain, build_code_analysis_stream_chain, normalize_analysis_output, parse_json_output
from backend.storage.history import get_history, save_history
from backend.tasks.analysis_tasks import run_code_analysis_task
from backend.tasks.celery_app import celery_app
from backend.tools.executor import run_python_code
from backend.tools.visualizer import estimate_complexity, generate_flowchart
from backend.utils.analysis import enrich_analysis_result, select_provider, compute_question_count

load_dotenv()

app = FastAPI(
    title="AI Code Explainer & Debugger",
    description="Analyse, debug, and improve code using LangChain-powered reasoning.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root() -> Dict[str, str]:
    """Return a basic health check for the service."""
    return {"status": "online", "service": "AI Code Explainer & Debugger"}


@app.get("/api/v1/analysis/{session_id}")
async def get_analysis_history(session_id: str) -> List[Dict[str, Any]]:
    """Retrieve the stored analysis history for a session."""
    history = get_history(session_id)
    if not history:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No analysis history found for session '{session_id}'.",
        )
    return history


@app.post("/api/v1/analysis/jobs", response_model=AnalysisJobResponse, status_code=status.HTTP_202_ACCEPTED)
async def submit_analysis_job(request: AnalysisJobRequest) -> AnalysisJobResponse:
    """Submit a code analysis job for background execution."""
    if not request.code.strip():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Code input cannot be empty.")

    task = run_code_analysis_task.delay(
        request.code,
        request.language,
        request.mode,
        request.session_id,
    )

    return AnalysisJobResponse(job_id=task.id, status=task.status)


@app.get("/api/v1/analysis/jobs/{job_id}", response_model=AnalysisJobStatus)
async def get_job_status(job_id: str) -> AnalysisJobStatus:
    """Get the current status for a submitted analysis job."""
    async_result = celery_app.AsyncResult(job_id)
    result = None
    if async_result.successful():
        result = async_result.result
    return AnalysisJobStatus(job_id=job_id, status=async_result.status, result=result)


def _build_response(result: dict[str, Any], code: str) -> dict[str, Any]:
    """Enrich the analysis result with execution, flowchart, and complexity details."""
    return enrich_analysis_result(result, code)


@app.post("/api/v1/analysis", response_model=AnalyseResponse, status_code=status.HTTP_201_CREATED)
async def create_analysis(request: AnalyseRequest) -> dict[str, Any]:
    """Analyse a code snippet and return structured explanation, fixes, and metrics."""
    if not request.code.strip():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Code input cannot be empty.")

    try:
        provider, api_key, model_name = select_provider()
        num_questions = compute_question_count(request.code)
        chain = build_code_analysis_chain(
            api_key,
            provider=provider,
            model_name=model_name,
            mode=request.mode,
            code=request.code,
        )
        raw_result = chain.invoke({
            "code": request.code,
            "language": request.language,
            "num_questions": num_questions,
        })

        result = normalize_analysis_output(raw_result, request.code, request.language)
        save_history(request.session_id, {"code": request.code, "result": result})
        return _build_response(result, request.code)
    except RuntimeError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc))


@app.post("/api/v1/analysis/stream")
async def stream_analysis(request: AnalyseRequest) -> StreamingResponse:
    """Stream analysis tokens back to the client via server-sent events."""
    if not request.code.strip():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Code input cannot be empty.")

    try:
        provider, api_key, model_name = select_provider()
        num_questions = compute_question_count(request.code)
        llm, prompt = build_code_analysis_stream_chain(
            api_key,
            provider=provider,
            model_name=model_name,
            mode=request.mode,
            code=request.code,
        )
        message_objects = prompt.format_messages(
            code=request.code,
            language=request.language,
            num_questions=num_questions,
        )

        def event_generator() -> Any:
            raw_stream_text = ""
            try:
                for event in llm.stream(message_objects):
                    token_text = getattr(event, "text", None)
                    if token_text is None:
                        token_text = getattr(event, "content", None)
                    if isinstance(token_text, list):
                        token_text = "".join(str(chunk) for chunk in token_text)
                    if token_text is None:
                        token_text = str(event)

                    if not token_text:
                        continue

                    raw_stream_text += token_text
                    yield f"event: token\ndata: {json.dumps({'token': token_text})}\n\n"
            except Exception as exc:
                yield f"event: error\ndata: {json.dumps({'error': str(exc)})}\n\n"
                return

            try:
                parsed_result = parse_json_output(raw_stream_text)
                normalized_result = normalize_analysis_output(parsed_result, request.code, request.language)
                yield f"event: done\ndata: {json.dumps({'result': normalized_result})}\n\n"
            except Exception as exc:
                yield f"event: error\ndata: {json.dumps({'error': f'Failed to parse streamed analysis result: {exc}'})}\n\n"

        return StreamingResponse(event_generator(), media_type="text/event-stream")
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc))


@app.post("/analyse", response_model=AnalyseResponse)
async def analyse_code_alias(request: AnalyseRequest) -> dict[str, Any]:
    """Legacy alias for the /api/v1/analysis endpoint."""
    return await create_analysis(request)


@app.post("/stream-analyse")
async def stream_analysis_alias(request: AnalyseRequest) -> StreamingResponse:
    """Legacy alias for the /api/v1/analysis/stream endpoint."""
    return await stream_analysis(request)
