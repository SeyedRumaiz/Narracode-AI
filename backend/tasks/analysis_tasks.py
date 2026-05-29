"""Background job tasks for AI code analysis."""

from typing import Any, Dict

from backend.chains import build_code_analysis_chain, normalize_analysis_output
from backend.storage.history import save_history
from backend.tasks.celery_app import celery_app
from backend.tools.executor import run_python_code
from backend.tools.visualizer import estimate_complexity, generate_flowchart
from backend.utils.analysis import compute_question_count, select_provider, enrich_analysis_result


@celery_app.task(bind=True, name="backend.tasks.analysis_tasks.run_code_analysis_task")
def run_code_analysis_task(
    self,
    code: str,
    language: str = "auto-detect",
    mode: str = "intermediate",
    session_id: str = "default",
) -> Dict[str, Any]:
    """Execute a code analysis job asynchronously and store session history."""
    provider, api_key, model_name = select_provider()
    num_questions = compute_question_count(code)

    chain = build_code_analysis_chain(
        api_key,
        provider=provider,
        model_name=model_name,
        mode=mode,
        code=code,
    )

    raw_result = chain.invoke({
        "code": code,
        "language": language,
        "num_questions": num_questions,
    })

    result = normalize_analysis_output(raw_result, code, language)
    enriched = enrich_analysis_result(result, code)

    save_history(session_id, {"code": code, "result": enriched, "task_id": self.request.id})
    return enriched
