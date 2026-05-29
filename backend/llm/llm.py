"""LLM chain construction and provider helpers for the AI Code Explainer backend."""

from typing import Any, Dict, List, Optional, Tuple

from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda

from .analysis_utils import parse_json_output, retrieve_relevant_docs
from .prompts import HUMAN_PROMPT, SYSTEM_PROMPT


def _build_system_prompt(code: str, mode: str = "intermediate", history: Optional[List[Dict[str, Any]]] = None) -> str:
    """Construct the system prompt text with optional mode and history context."""
    prompt_text = SYSTEM_PROMPT
    if mode:
        prompt_text += f"\n\nExplain the code in {mode} mode. "
        if mode == 'beginner':
            prompt_text += 'Use simple language, concrete examples, and step-by-step metaphors.'
        if mode == 'expert':
            prompt_text += 'Use technical terminology, complexity reasoning, and optimization tradeoffs.'

    if history:
        prompt_text += "\n\nPrevious conversation context:\n"
        for entry in history[-2:]:
            prompt_text += f"Code:\n{entry.get('code', '')}\nAnalysis Summary:\n{entry.get('result', {}).get('explanation', '')}\n"

    return prompt_text


def get_llm(provider: str, api_key: str, model_name: Optional[str] = None, streaming: bool = False) -> ChatOpenAI:
    """Create an LLM client instance for the configured provider."""
    if provider == "ollama":
        return ChatOpenAI(
            model=model_name or "qwen2.5-coder:1.5b",
            base_url="http://localhost:11434/v1",
            api_key="ollama",
            temperature=0.2,
            max_tokens=4096,
            streaming=streaming,
        )

    if provider == "deepseek":
        return ChatOpenAI(
            model="deepseek-chat",
            api_key=api_key,
            base_url="https://api.deepseek.com/v1",
            temperature=0.2,
            streaming=streaming,
        )

    if provider == "openai":
        return ChatOpenAI(
            model=model_name or "gpt-4o",
            api_key=api_key,
            temperature=0.2,
            streaming=streaming,
        )

    raise ValueError("Unsupported provider")


def build_code_analysis_chain(
    api_key: str,
    provider: str = "openai",
    model_name: Optional[str] = None,
    mode: str = "intermediate",
    history: Optional[List[Dict[str, Any]]] = None,
    code: Optional[str] = None,
) -> Any:
    """Build the analysis chain used by the non-streaming /analyse endpoint."""
    llm = get_llm(provider, api_key, model_name)
    docs = retrieve_relevant_docs(code or "", mode)
    system_prompt = _build_system_prompt(code or "", mode, history)
    if docs:
        system_prompt += "\n\nUse these framework/technology notes if applicable:\n"
        system_prompt += "\n".join(docs)

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", HUMAN_PROMPT),
    ])

    chain = (
        prompt
        | llm
        | StrOutputParser()
        | RunnableLambda(parse_json_output)
    )

    return chain


def build_code_analysis_stream_chain(
    api_key: str,
    provider: str = "openai",
    model_name: Optional[str] = None,
    mode: str = "intermediate",
    history: Optional[List[Dict[str, Any]]] = None,
    code: Optional[str] = None,
) -> Tuple[ChatOpenAI, ChatPromptTemplate]:
    """Build the analysis chain used by the streaming /stream-analyse endpoint."""
    llm = get_llm(provider, api_key, model_name, streaming=True)
    docs = retrieve_relevant_docs(code or "", mode)
    system_prompt = _build_system_prompt(code or "", mode, history)
    if docs:
        system_prompt += "\n\nUse these framework/technology notes if applicable:\n"
        system_prompt += "\n".join(docs)

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", HUMAN_PROMPT),
    ])

    return llm, prompt


__all__ = [
    "get_llm",
    "build_code_analysis_chain",
    "build_code_analysis_stream_chain",
]
