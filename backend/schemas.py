from pydantic import BaseModel

class AnalyseRequest(BaseModel):
    code: str
    language: str = "auto-detect"
    session_id: str = "default"


class AnalyseResponse(BaseModel):
    language: str
    explanation: str
    bugs: list
    fixed_code: str
    flowchart: str
    complexity: dict
    execution_output: str
    questions: list
