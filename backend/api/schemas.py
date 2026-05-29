from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class AnalyseRequest(BaseModel):
    """Request model for code analysis requests."""

    code: str
    language: str = "auto-detect"
    mode: str = "intermediate"
    session_id: str = "default"


class AnalyseResponse(BaseModel):
    """Structured response model for code analysis results."""

    language: str = ""
    explanation: str = ""
    story: str = ""
    bugs: List[Dict[str, Any]] = Field(default_factory=list)
    fixed_code: str = ""
    improvements: List[str] = Field(default_factory=list)
    questions: List[Dict[str, Any]] = Field(default_factory=list)
    time_complexity: str = ""
    space_complexity: str = ""
    complexity_explanation: str = ""
    docstring: str = ""
    unit_tests: str = ""
    flowchart: str = ""
    complexity: Dict[str, Any] = Field(default_factory=dict)
    execution_output: Dict[str, Any] = Field(default_factory=dict)
    optimized_code: str = ""
    optimization_comparison: str = ""
    optimized_time_complexity: str = ""
    optimized_space_complexity: str = ""
    optimized_complexity: Dict[str, Any] = Field(default_factory=dict)


class AnalysisJobRequest(AnalyseRequest):
    """Request model for async analysis job submissions."""


class AnalysisJobResponse(BaseModel):
    """Response returned when a job is created."""

    job_id: str
    status: str = "pending"


class AnalysisJobStatus(BaseModel):
    """Status response for an async analysis job."""

    job_id: str
    status: str
    result: Optional[AnalyseResponse] = None
