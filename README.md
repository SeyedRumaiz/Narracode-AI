# 🚀 AI Code Explainer & Debugger

> A full-stack code analysis toolkit with a REST API backend and responsive browser experience.

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

## Key features

- **REST-first backend**: resource-oriented `/api/v1/analysis` routes
- **Streaming analysis**: tokens delivered incrementally for responsive UI feedback
- **Bug detection**: syntax and logic issue discovery with severity hints
- **Auto fixes**: corrected code suggestions and optimized alternatives
- **Complexity insights**: time/space estimates plus performance commentary
- **Flowchart generation**: visual execution path rendering via Mermaid
- **Docstrings & tests**: generated Python documentation and unit test scaffolding
- **Responsive UI**: mobile-friendly layout, hover interactions, and real-time stream display

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

## API overview

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

### Streaming analysis

`POST /api/v1/analysis/stream`

The streaming endpoint returns server-sent events containing token payloads as the LLM generates the JSON analysis output.

### Session history

`GET /api/v1/analysis/{session_id}`

Retrieve the most recent analysis records for a given session ID.

---

## Environment variables

Create a `.env` file in the root or `backend/` directory with the following values:

```bash
OPENAI_API_KEY=your_openai_key
DEEPSEEK_API_KEY=your_deepseek_key
OLLAMA_MODEL=qwen2.5-coder:1.5b
```

> If you use Ollama locally, set `OLLAMA_MODEL` to the model name available on your machine.

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
