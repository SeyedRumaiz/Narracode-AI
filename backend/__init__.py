"""Backend package for AI Code Explainer modules."""

from .llm import build_code_analysis_chain, build_code_analysis_stream_chain, get_llm
from .llm.analysis_utils import normalize_analysis_output
from .llm.prompts import SYSTEM_PROMPT, HUMAN_PROMPT

__all__ = [
    "build_code_analysis_chain",
    "build_code_analysis_stream_chain",
    "normalize_analysis_output",
    "get_llm",
    "SYSTEM_PROMPT",
    "HUMAN_PROMPT",
]
