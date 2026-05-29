# 🚀 AI Code Explainer & Debugger

An AI-powered backend system that analyzes, debugs, explains, and improves code using LLMs via LangChain + FastAPI.

## 🧠 Overview

This project turns any code snippet into a complete learning + debugging experience.

It behaves like a:
- Senior software engineer 👨‍💻
- Programming tutor 📚
- Code reviewer 🐞
- Interview trainer 🎯
- System designer 🏗️

You input code → it returns a full AI-powered breakdown.

## What this repo contains

This repository bundles a local AI code analysis prototype with:

- **Backend**: Python + FastAPI + LangChain analysis engine
- **Frontend**: responsive HTML/CSS/JS interface for interactive code review
- **REST API**: structured `/api/v1/analysis` endpoints and streaming support
- **Session persistence**: lightweight in-memory session history for repeated analysis
- **Code utilities**: execution sandbox, flowchart visualization, and complexity estimation

---

## Folder structure

```text
ai-code-explainer/
├── Makefile
├── README.md
├── backend/
│   ├── api/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   └── schemas.py
│   ├── llm/
│   │   ├── __init__.py
│   │   ├── agents.py
│   │   ├── analysis_utils.py
│   │   ├── llm.py
│   │   └── prompts.py
│   ├── storage/
│   │   ├── __init__.py
│   │   └── memory.py
│   ├── tools/
│   │   ├── executor.py
│   │   └── visualizer.py
│   ├── __init__.py
│   ├── chains.py
│   ├── main.py
│   ├── requirements.txt
│   └── tests/
│       └── ...
├── frontend/
│   ├── app.js
│   ├── index.html
│   └── style.css
├── CONTRIBUTING.md
└── LICENSE
```

- `backend/api/` defines REST resources and request/response schemas.
- `backend/llm/` contains language model helpers, prompt scaffolding, and output normalization.
- `backend/storage/` keeps per-session analysis history in memory.
- `backend/tools/` contains runtime helpers for flowcharts and safe code execution.
- `frontend/` provides the browser UI with live streaming and result panels.

---

## ✨ Key Features

1. **AI Code Analysis**
   - Detects programming language automatically
   - Explains code in simple human language
   - Breaks down logic step-by-step

2. **Bug Detection System**
   Detects:
   - Syntax errors
   - Logical errors
   - Performance issues
   - Security vulnerabilities
   - Bad coding style
   Each bug includes:
   - Line number
   - Type
   - Description
   - Severity (Low / Medium / High / Critical)

3. **Auto Code Fixing**
   - Produces corrected, runnable code
   - Keeps original logic intact
   - Provides optimized, production-ready output

4. **Complexity Analysis**
   - Time complexity (Big-O)
   - Space complexity
   - Detailed reasoning and explanation
   Examples:
   - O(1)
   - O(n)
   - O(n log n)
   - O(n²)

5. **Story-Based Explanation Mode**
   - Transforms code into a story
   - Variables become characters
   - Functions become actions
   - Execution becomes a journey
   - Helps beginners understand faster

6. **AI Question Generator**
   - Generates interview/viva questions
   - Provides answers for each question
   - Difficulty adapts to code length

7. **Flowchart Generator**
   - Converts code logic into a flow representation
   - Helps visualize execution steps

8. **Code Execution Engine**
   - Safely runs Python code
   - Returns output, errors, and execution status

9. **Documentation Generator**
   - Automatically creates function docstrings
   - Generates code documentation blocks
   - Produces clean API-style descriptions

10. **Unit Test Generator**
    - Generates pytest-style test cases
    - Covers edge cases and error handling
    - Includes normal scenario coverage

11. **Memory System**
    - Stores previous analyses per session
    - Enables contextual improvements
    - Supports learning history tracking

---

## ⚙️ Tech Stack

- FastAPI – Backend framework
- LangChain – LLM orchestration
- Ollama / DeepSeek / OpenAI – LLM providers
- Pydantic – Data validation
- Python Sandbox Executor – Code execution layer
- Custom Visualizer Module – Flowcharts & complexity analysis
- Memory Module – Session persistence

---

## 🤖 Supported AI Models

- 🟢 Local Models (Ollama)
  - `qwen2.5-coder`
  - `llama3`
  - `codellama`

- 🔵 API Models
  - DeepSeek Chat API
  - OpenAI models via `OPENAI_API_KEY`

---

## 📡 API Endpoints

### Health check

`GET /`

Example response:

```json
{
  "status": "online",
  "service": "AI Code Explainer & Debugger"
}
```

### Create analysis

`POST /api/v1/analysis`

Request body:

```json
{
  "code": "print('Hello World')",
  "language": "auto-detect",
  "mode": "intermediate",
  "session_id": "user123"
}
```

Example response:

```json
{
  "language": "python",
  "explanation": "Prints Hello World to the console.",
  "story": "A message travels through the program...",
  "bugs": [],
  "fixed_code": "print('Hello World')",
  "improvements": [
    "Add error handling",
    "Use logging instead of print"
  ],
  "questions": [
    {
      "question": "What does print() do?",
      "answer": "It outputs data to the console."
    }
  ],
  "time_complexity": "O(1)",
  "space_complexity": "O(1)",
  "complexity_explanation": "No loops or recursion used.",
  "docstring": "\"\"\"Prints a message to console\"\"\"",
  "unit_tests": "def test_output(): assert True",
  "flowchart": "START → PRINT → END",
  "execution_output": {
    "output": "Hello World"
  }
}
```

### Create analysis alias

`POST /analyse`

This is a legacy alias for `/api/v1/analysis`.

### Streaming analysis

`POST /api/v1/analysis/stream`

The streaming endpoint returns server-sent events containing token payloads as the LLM generates the JSON analysis output.

### Async job submission

`POST /api/v1/analysis/jobs`

Submit a background analysis job. The request body is the same as `POST /api/v1/analysis`.

Example response:

```json
{
  "job_id": "<celery-task-id>",
  "status": "PENDING"
}
```

### Async job status

`GET /api/v1/analysis/jobs/{job_id}`

Poll the job for completion and retrieve the final result when available.

### Session history

`GET /api/v1/analysis/{session_id}`

Retrieve the most recent analysis records for a given session ID.

---

## Getting started

### 1. Setup environment

```bash
cd /Users/seyedrumaiz/Desktop/ai-code-explainer
make setup
```

### 2. Install backend dependencies

```bash
make install-backend
```

### 3. Launch the backend

```bash
make run-backend
```

### 4. Serve the frontend

```bash
make run-frontend
```

### 5. Open the app

- Frontend: `http://127.0.0.1:5500`
- API docs: `http://127.0.0.1:8000/docs`

---

## Environment variables

Create a `.env` file in the root or `backend/` directory with the following values:

```bash
OPENAI_API_KEY=your_openai_key
OPENAI_MODEL=gpt-4o
DEEPSEEK_API_KEY=your_deepseek_key
DEEPSEEK_MODEL=deepseek-chat
OLLAMA_MODEL=qwen2.5-coder:1.5b
ANALYSIS_TIMEOUT=60
```

> If you use Ollama locally, set `OLLAMA_MODEL` to the model name available on your machine.
>
> `ANALYSIS_TIMEOUT` controls how long the backend waits for the LLM provider before returning a 504.

---

## Useful commands

- `make setup` — create the virtualenv and install backend dependencies
- `make install-backend` — install backend Python packages
- `make run-backend` — start the FastAPI server
- `make run-api` — start the backend from `backend/api/main.py`
- `make run-frontend` — serve static frontend files
- `make check` — syntax-check backend Python files
- `make test` — run backend test cases
- `make clean` — remove the virtualenv and compiled Python caches

---

## Notes

- The primary backend entrypoint is `backend/api/main.py`.
- `backend/main.py` remains available as a compatibility wrapper.
- The frontend is static and communicates with the backend via REST requests.
- This repo is best used as a development prototype; production deployment should add auth and persistent storage.

---

## License

This repository is provided as-is for experimentation and development.
