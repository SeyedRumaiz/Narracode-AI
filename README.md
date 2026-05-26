# 🚀 AI Code Explainer & Debugger

> An AI-powered backend system that analyzes, debugs, explains, and improves code using LLMs via LangChain + FastAPI.

---

# 🧠 Overview

This project turns any code snippet into a **complete learning + debugging experience**.

It behaves like a:
- Senior software engineer 👨‍💻
- Programming tutor 📚
- Code reviewer 🐞
- Interview trainer 🎯
- System designer 🏗️

You input code → it returns a full AI-powered breakdown.

---

# ✨ Key Features

## 🔍 1. AI Code Analysis
- Detects programming language automatically
- Explains code in simple human language
- Breaks down logic step-by-step

---

## 🐞 2. Bug Detection System
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

---

## 🛠 3. Auto Code Fixing
- Produces corrected, runnable code
- Keeps original logic intact
- Optimized and production-ready output

---

## 📊 4. Complexity Analysis
- Time complexity (Big-O)
- Space complexity
- Detailed explanation of reasoning

Examples:
- O(1)
- O(n)
- O(n log n)
- O(n²)

---

## 🧠 5. Story-Based Explanation Mode
Transforms code into a story:
- Variables become characters
- Functions become actions
- Execution becomes a journey

👉 Helps beginners understand faster

---

## ❓ 6. AI Question Generator
- Generates interview/viva questions
- Provides answers for each question
- Difficulty adapts to code length

---

## 📈 7. Flowchart Generator
- Converts code logic into flow representation
- Helps visualize execution steps

---

## 🧪 8. Code Execution Engine
- Safely runs Python code
- Returns:
  - Output
  - Errors
  - Execution status

---

## 🧾 9. Documentation Generator
Automatically creates:
- Function docstrings
- Code documentation blocks
- Clean API-style descriptions

---

## 🧪 10. Unit Test Generator
Generates:
- pytest-style test cases
- Edge cases
- Error handling tests
- Normal scenario coverage

---

## 💾 11. Memory System
- Stores previous analyses per session
- Enables contextual improvements
- Supports learning history tracking

---

# ⚙️ Tech Stack

- **FastAPI** – Backend framework
- **LangChain** – LLM orchestration
- **Ollama / DeepSeek** – LLM providers
- **Pydantic** – Data validation
- **Python Sandbox Executor** – Code execution layer
- **Custom Visualizer Module** – Flowcharts & complexity analysis
- **Memory Module** – Session persistence

---

# 🤖 Supported AI Models

## 🟢 Local Models (Ollama)
- qwen2.5-coder
- llama3
- codellama

## 🔵 API Models
- DeepSeek Chat API

---

# 📡 API Endpoints

## 🟢 GET `/`
Check if backend is running.

```json
{
  "status": "online",
  "service": "AI Code Explainer & Debugger"
}
```
## 🔵 POST /analyse
# Request
```json
{
  "code": "print('Hello World')",
  "language": "auto-detect",
  "session_id": "user123"
}
```

# Response
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

# 🔐 Environment Variables

Create a .env file:
```bash
OPENAI_API_KEY=your_key_here
DEEPSEEK_API_KEY=your_key_here
OLLAMA_MODEL=qwen2.5-coder:1.5b
```

# 🚀 Installation & Setup

## 1. Clone project
```bash
git clone https://github.com/your-username/ai-code-explainer.git
cd ai-code-explainer/backend
```

## 2. Create virtual environment
```bash
python -m venv venv
source venv/bin/activate   # Mac/Linux
venv\Scripts\activate      # Windows
```

## 3. Install dependencies
```bash
pip install -r requirements.txt
```

## 4. Run server
```bash
uvicorn main:app --reload --port 8000
```

## 5. Open API docs
```bash
http://127.0.0.1:8000/docs
```