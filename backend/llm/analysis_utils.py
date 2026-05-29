"""Utility helpers for code analysis output normalization and code inspection."""

from __future__ import annotations

import ast
import importlib.util
import json
import re
from typing import Any, Dict, List, Optional

json_repair_spec = importlib.util.find_spec("json_repair")
json_repair = importlib.util.module_from_spec(json_repair_spec) if json_repair_spec else None
if json_repair_spec is not None:
    json_repair_spec.loader.exec_module(json_repair)

EXPECTED_OUTPUT_KEYS: Dict[str, Any] = {
    "language": "",
    "explanation": "",
    "story": "",
    "bugs": [],
    "fixed_code": "",
    "improvements": [],
    "questions": [],
    "time_complexity": "",
    "space_complexity": "",
    "complexity_explanation": "",
    "docstring": "",
    "unit_tests": "",
    "optimized_code": "",
    "optimization_comparison": "",
    "optimized_time_complexity": "",
    "optimized_space_complexity": "",
}

KEY_SYNONYMS: Dict[str, str] = {
    "documentation": "docstring",
    "documentation_block": "docstring",
    "documentation_string": "docstring",
    "tests": "unit_tests",
    "test_suite": "unit_tests",
    "test_code": "unit_tests",
    "python_tests": "unit_tests",
    "optimizedCode": "optimized_code",
    "optimization_comparison": "optimization_comparison",
    "optimizedTimeComplexity": "optimized_time_complexity",
    "optimizedSpaceComplexity": "optimized_space_complexity",
    "complexityExplanation": "complexity_explanation",
    "timeComplexity": "time_complexity",
    "spaceComplexity": "space_complexity",
}


def parse_json_output(text: str) -> Dict[str, Any]:
    """Parse the LLM JSON output while stripping markdown fences and repairing malformed JSON."""
    cleaned = text.strip()
    if cleaned.startswith("```"):
        lines = cleaned.splitlines()
        cleaned = "\n".join(lines[1:-1]) if lines[-1].strip() == "```" else "\n".join(lines[1:])

    def repl(match: re.Match[str]) -> str:
        return ": " + json.dumps(match.group(1))

    cleaned = re.sub(r":\s*\"\"\"(.*?)\"\"\"\s*(?=,|\})", repl, cleaned, flags=re.DOTALL)
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        if json_repair is not None:
            return json_repair.repair_json(cleaned, return_objects=True)
        raise


def strip_markdown_fences(text: Any) -> Any:
    """Remove code fences from a string, preserving raw code/text."""
    if not isinstance(text, str):
        return text
    cleaned = text.strip()
    if cleaned.startswith('```'):
        lines = cleaned.splitlines()
        if len(lines) >= 2 and lines[-1].strip() == '```':
            cleaned = '\n'.join(lines[1:-1])
        else:
            cleaned = '\n'.join(lines[1:])
    return cleaned.strip()


def is_google_docstring(text: Any) -> bool:
    """Return True when the text resembles a Python Google-style docstring."""
    if not isinstance(text, str):
        return False
    return bool(re.search(r"\bArgs:\b", text)) and bool(re.search(r"\bReturns:\b", text))


def parse_python_functions(code: str) -> List[Dict[str, Any]]:
    """Extract top-level Python function signatures and return metadata from source code."""
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return []

    functions: List[Dict[str, Any]] = []
    for node in tree.body:
        if isinstance(node, ast.FunctionDef):
            args: List[str] = [arg.arg for arg in node.args.args if arg.arg not in {'self', 'cls'}]
            defaults: Dict[str, str] = {}
            defaults_list = [ast.unparse(d) for d in node.args.defaults] if node.args.defaults else []
            if defaults_list:
                for arg_name, default_value in zip(args[-len(defaults_list) :], defaults_list):
                    defaults[arg_name] = default_value

            returns = ast.unparse(node.returns) if node.returns is not None else ''
            functions.append({
                'name': node.name,
                'args': args,
                'defaults': defaults,
                'returns': returns,
                'docstring': ast.get_docstring(node) or ''
            })
    return functions


def retrieve_relevant_docs(code: str, language: str = "python") -> List[str]:
    """Return a small set of technology notes or hints based on code characteristics."""
    snippets: List[str] = []
    if 'useState' in code or 'React' in code or 'useEffect' in code:
        snippets.append('React hooks are functions that let you use state and lifecycle features from function components. useState returns a state value and a setter callback.')
    if 'async' in code and 'await' in code:
        snippets.append('Async/await syntax in JavaScript lets asynchronous code read like synchronous code by awaiting Promises.')
    if 'numpy' in code or 'pandas' in code:
        snippets.append('NumPy arrays and pandas DataFrames are optimized for vectorized computations and avoid Python-level loops when possible.')
    if 'def ' in code and 'return' in code and 'lambda' not in code:
        snippets.append('In Python, top-level functions should have clear parameter names and return statements to make testing and documentation easier.')
    if 'class ' in code and 'extends' in code:
        snippets.append('In JavaScript/TypeScript, classes use extends for inheritance and constructors should call super() when inheriting.')
    return snippets


def detect_code_language(code: str, language: str = "python") -> str:
    """Detect the programming language of a code snippet or use a provided hint."""
    base = (language or "python").lower()
    if base in {"auto", "auto-detect", "auto_detect", "detect"}:
        if re.search(r"\bdef\s+[A-Za-z0-9_]+\s*\(", code):
            return "python"
        if re.search(r"\b(function|const|let|var)\b", code):
            return "javascript"
        if re.search(r"#include\s+<|std::|\bprintf\b", code):
            return "cpp"
        if re.search(r"\bpublic\s+class\b|System\.out\.println", code):
            return "java"
        return "python"
    return base


def generate_docstring(code: str, language: str = "python") -> str:
    """Generate a placeholder docstring for Python or JS/TS code."""
    language = detect_code_language(code, language)
    if "python" in language:
        functions = parse_python_functions(code)
        if functions:
            func = functions[0]
            lines = ['"""']
            lines.append(f"{func['name']} description goes here.")
            lines.append("")
            if func['args']:
                lines.append("Args:")
                for arg in func['args']:
                    default = func['defaults'].get(arg)
                    if default is not None:
                        lines.append(f"    {arg} (Any): DESCRIPTION. Defaults to {default}.")
                    else:
                        lines.append(f"    {arg} (Any): DESCRIPTION.")
                lines.append("")
            if func['returns']:
                lines.append("Returns:")
                lines.append(f"    {func['returns']}: DESCRIPTION.")
                lines.append("")
            lines.append('"""')
            return "\n".join(lines)
        return '"""Auto-generated documentation for this Python code snippet.\n\nReplace the summary and parameter descriptions with actual behavior from your code.\n"""'
    if "javascript" in language or "typescript" in language:
        return "/**\n * Auto-generated documentation for this code snippet.\n * Replace with actual parameter descriptions and return values.\n */"
    return "<Generated documentation not available for this language>"


def generate_unit_tests(code: str, language: str = "python") -> str:
    """Generate a minimal unit test scaffold for detected functions."""
    language = detect_code_language(code, language)
    if "python" in language:
        functions = parse_python_functions(code)
        if functions:
            tests: List[str] = ["import pytest\n\n"]
            imported = False
            for func in functions:
                if not imported:
                    tests.append(f"from your_module import {func['name']}\n\n")
                    imported = True
                test_args: List[str] = []
                for arg in func['args']:
                    default = func['defaults'].get(arg)
                    if default is not None:
                        test_args.append(default)
                    elif arg.startswith('is_') or arg.startswith('has_'):
                        test_args.append('False')
                    elif arg.startswith('num') or arg.endswith('count') or arg.endswith('size'):
                        test_args.append('0')
                    else:
                        test_args.append('None')
                args_str = ", ".join(test_args)
                tests.append(f"def test_{func['name']}_basic():\n")
                tests.append(f"    # TODO: replace with expected result for {func['name']}\n")
                tests.append(f"    result = {func['name']}({args_str})\n")
                tests.append(f"    assert result == ...\n\n")
            return "".join(tests)
        return (
            "# No explicit function was detected in the code snippet.\n"
            "# Add assertions for the expected behavior of this code.\n\n"
            "def test_sample_behavior():\n"
            "    assert True\n"
        )
    if "javascript" in language or "typescript" in language:
        return (
            "import { describe, it, expect } from 'vitest';\n\n"
            "describe('Auto-generated tests', () => {\n"
            "  it('should validate a sample behavior', () => {\n"
            "    expect(true).toBe(true);\n"
            "  });\n"
            "});\n"
        )
    return "# Unit test generation is not available for this language."


def normalize_analysis_output(raw_output: Dict[str, Any], code: str, language: str = "python") -> Dict[str, Any]:
    """Normalize analysis output to expected keys and generate missing docstrings/tests."""
    normalized: Dict[str, Any] = {}
    for key, value in raw_output.items():
        mapped_key = KEY_SYNONYMS.get(key, key)
        normalized[mapped_key] = value

    for key, default in EXPECTED_OUTPUT_KEYS.items():
        if key not in normalized or normalized[key] is None:
            normalized[key] = default
        elif isinstance(normalized[key], str):
            normalized[key] = strip_markdown_fences(normalized[key])

    if not normalized["docstring"] or ("python" in detect_code_language(code, language) and not is_google_docstring(normalized["docstring"])):
        normalized["docstring"] = generate_docstring(code, language)

    if not normalized["unit_tests"]:
        normalized["unit_tests"] = generate_unit_tests(code, language)

    if not normalized["optimized_time_complexity"]:
        normalized["optimized_time_complexity"] = normalized.get("time_complexity", "")
    if not normalized["optimized_space_complexity"]:
        normalized["optimized_space_complexity"] = normalized.get("space_complexity", "")

    return normalized
