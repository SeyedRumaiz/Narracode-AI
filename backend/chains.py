"""
LangChain pipeline: prompt → LLM → structured JSON output.
"""

import json
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate   # Structured prompts
from langchain_core.output_parsers import StrOutputParser

# Lets us insert a custom Python function inside the LangChain pipeline
from langchain_core.runnables import RunnableLambda
import json_repair  # To fix malformed JSON
from fastapi.responses import StreamingResponse

# System prompt for structured analysis
SYSTEM_PROMPT = """You are an elite software engineer and debugging expert. 
When given a code snippet your job is to analyse it and return a strict JSON object 
(no markdown fences, no extra text) with the following keys:

{{
  "language": "<detected programming language>",
  "explanation": "<clear, concise paragraph explaining what the code does>",
  "story": "<an engaging, creative story explaining the code line-by-line using metaphors or a narrative format (e.g., tracking a variable or data flow as a character on a quest/adventure)>",
  "bugs": [
    {{
      "line": <line number or null>,
      "type": "<Syntax | Logic | Performance | Security | Style>",
      "description": "<what the bug is>",
      "severity": "<Critical | High | Medium | Low>"
    }}
  ],
  "fixed_code": "<the corrected, production-ready version of the code>",
  "improvements": [
    "<actionable improvement suggestion 1>",
    "<actionable improvement suggestion 2>"
  ],
  "questions": [
    {{
      "question": "<conceptual, logical, or comprehension question about this code>",
      "answer": "<clear, informative answer explaining the logic, variable state, or output>"
    }}
  ],
  "time_complexity": "<Time complexity, e.g., O(1), O(log n), O(n), O(n log n), O(n^2), O(2^n)>",
  "space_complexity": "<Space complexity, e.g., O(1), O(log n), O(n), O(n^2)>",
  "complexity_explanation": "<concise explanation of how the time and space complexity were calculated>",
  "docstring": "<complete, correctly formatted docstring/documentation block for the main function(s) based on standard conventions (e.g., Python Google-style, JSDoc for JS/TS)>",
  "unit_tests": "<a complete, runnable unit test suite (e.g., using pytest, Jest, testing package) covering typical inputs, boundary/edge cases, and error cases>"
}}

Rules:
- If there are no bugs, return an empty array for "bugs".
- "fixed_code" must always contain complete, runnable code.
- Return ONLY raw JSON — no markdown, no commentary outside the JSON.
"""

HUMAN_PROMPT = """Language hint: {language}
Generate exactly {num_questions} questions and answers in the "questions" array.

Code to analyse:
```
{code}
```"""


# Output parser: JSON string to Python dict
def parse_json_output(text: str) -> dict:
    """Strip any accidental markdown fences and parse JSON robustly."""
    cleaned = text.strip()
    # Remove ```json ... ``` or ``` ... ``` wrappers if present
    if cleaned.startswith("```"):
        lines = cleaned.splitlines()
        cleaned = "\n".join(lines[1:-1]) if lines[-1].strip() == "```" else "\n".join(lines[1:])
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        return json_repair.repair_json(cleaned, return_objects=True)
    
def get_llm(provider, api_key, model_name=None):

    if provider == "ollama":
        return ChatOpenAI(
            model=model_name or "qwen2.5-coder:1.5b",
            base_url="http://localhost:11434/v1",
            api_key="ollama",
            temperature=0.2,
        )

    if provider == "deepseek":
        return ChatOpenAI(
            model="deepseek-chat",
            api_key=api_key,
            base_url="https://api.deepseek.com/v1",
            temperature=0.2,
        )

    raise ValueError("Unsupported provider")


def build_code_analysis_chain(api_key: str, provider: str = "openai", model_name: str = None):

    llm = get_llm(provider, api_key, model_name)

    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        ("human", HUMAN_PROMPT),
    ])

    chain = (
        prompt
        | llm
        | StrOutputParser()
        | RunnableLambda(parse_json_output)
    )

    return chain
