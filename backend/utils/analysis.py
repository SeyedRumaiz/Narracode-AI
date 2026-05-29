"""Shared analysis utilities for provider selection and result enrichment."""

import os
from typing import Any, Dict, Optional, Tuple

from dotenv import load_dotenv
from backend.tools.executor import run_python_code
from backend.tools.visualizer import estimate_complexity, generate_flowchart

load_dotenv()


def select_provider() -> Tuple[str, str, Optional[str]]:
    """Select the configured LLM provider and return provider details."""
    ollama_model = os.getenv("OLLAMA_MODEL", "")
    deepseek_model = os.getenv("DEEPSEEK_MODEL", "")
    deepseek_key = os.getenv("DEEPSEEK_API_KEY", "")
    openai_key = os.getenv("OPENAI_API_KEY", "")
    openai_model = os.getenv("OPENAI_MODEL", "")

    has_ollama = bool(ollama_model and ollama_model.strip())
    has_deepseek = bool(deepseek_key and deepseek_key.strip())
    has_openai = bool(openai_key and openai_key.strip())

    if has_ollama:
        return "ollama", "ollama", ollama_model
    if has_deepseek:
        return "deepseek", deepseek_key, deepseek_model
    if has_openai:
        return "openai", openai_key, openai_model or None

    raise RuntimeError(
        "No LLM providers configured. Please set OLLAMA_MODEL, DEEPSEEK_API_KEY, or OPENAI_API_KEY in backend/.env",
    )


def compute_question_count(code: str) -> int:
    """Choose how many follow-up questions to generate based on snippet length."""
    line_count = len(code.strip().splitlines())
    if line_count <= 10:
        return 5
    if line_count <= 20:
        return 7
    return 10


def enrich_analysis_result(result: Dict[str, Any], code: str) -> Dict[str, Any]:
    """Enrich the analysis result with execution, flowchart, and complexity details."""
    execution_output = run_python_code(code)
    flowchart = generate_flowchart(code)
    complexity = estimate_complexity(code)

    if not result.get("time_complexity"):
        result["time_complexity"] = complexity.get("time", "O(1)")
    if not result.get("space_complexity"):
        result["space_complexity"] = complexity.get("space", "O(1)")

    optimized_complexity = (
        estimate_complexity(result.get("optimized_code", ""))
        if result.get("optimized_code")
        else {
            "time": result.get("optimized_time_complexity", result.get("time_complexity", "O(1)")),
            "space": result.get("optimized_space_complexity", result.get("space_complexity", "O(1)")),
            "explanation": "Optimized complexity inferred from available output.",
        }
    )

    if not result.get("optimized_time_complexity"):
        result["optimized_time_complexity"] = optimized_complexity.get("time", result.get("time_complexity", "O(1)"))
    if not result.get("optimized_space_complexity"):
        result["optimized_space_complexity"] = optimized_complexity.get("space", result.get("space_complexity", "O(1)"))

    return {
        **result,
        "execution_output": execution_output,
        "flowchart": flowchart,
        "complexity": complexity,
        "optimized_complexity": optimized_complexity,
    }
