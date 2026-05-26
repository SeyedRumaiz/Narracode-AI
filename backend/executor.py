import subprocess
import tempfile
import os

def run_python_code(code: str):
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".py") as f:
            f.write(code.encode())
            file_path = f.name

        result = subprocess.run(
            ["python", file_path],
            capture_output=True,
            text=True,
            timeout=5
        )

        os.remove(file_path)

        return {
            "stdout": result.stdout,
            "stderr": result.stderr
        }

    except Exception as e:
        return {"error": str(e)}
