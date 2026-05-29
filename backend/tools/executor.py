"""Executor for safely running Python code snippets in a temporary file."""

import os
import subprocess
import tempfile
from typing import Any, Dict


def run_python_code(code: str) -> Dict[str, Any]:
    """Execute Python code in a temporary file and capture its stdout/stderr."""
    file_path = ''
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.py', mode='w', encoding='utf-8') as temp_file:
            temp_file.write(code)
            file_path = temp_file.name

        result = subprocess.run(
            ["python", file_path],
            capture_output=True,
            text=True,
            timeout=5,
        )

        return {
            'stdout': result.stdout,
            'stderr': result.stderr,
        }
    except Exception as exc:
        return {'error': str(exc)}
    finally:
        if file_path and os.path.exists(file_path):
            os.remove(file_path)
