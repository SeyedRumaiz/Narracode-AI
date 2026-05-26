# AI Code Explainer & Debugger
# Root Makefile for common development tasks.

PYTHON ?= python3
VENV_DIR ?= venv
PIP ?= $(VENV_DIR)/bin/pip
PYTHON_BIN ?= $(VENV_DIR)/bin/python
UVICORN ?= $(VENV_DIR)/bin/uvicorn
BACKEND_DIR ?= backend
FRONTEND_DIR ?= frontend
REQUIREMENTS ?= $(BACKEND_DIR)/requirements.txt

.PHONY: help setup install-backend run-backend run-frontend check clean

help:
	@echo "Available commands:"
	@echo "  make setup           # Create virtualenv and install backend dependencies"
	@echo "  make install-backend # Install backend dependencies into $(VENV_DIR)"
	@echo "  make run-backend     # Start FastAPI backend on http://127.0.0.1:8000"
	@echo "  make run-frontend    # Start a local static file server for frontend"
	@echo "  make check           # Syntax-check backend Python sources"
	@echo "  make clean           # Remove virtualenv and Python cache files"

setup: $(VENV_DIR)/bin/activate install-backend

$(VENV_DIR)/bin/activate:
	$(PYTHON) -m venv $(VENV_DIR)
	@echo "Virtual environment created at $(VENV_DIR)"

install-backend: $(VENV_DIR)/bin/activate
	$(PIP) install --upgrade pip
	$(PIP) install -r $(REQUIREMENTS)
	@echo "Backend dependencies installed"

run-backend: $(VENV_DIR)/bin/activate
	$(UVICORN) $(BACKEND_DIR).main:app --reload --host 127.0.0.1 --port 8000

run-frontend:
	@echo "Serving frontend from $(FRONTEND_DIR)"
	cd $(FRONTEND_DIR) && $(PYTHON) -m http.server 5500

check: $(VENV_DIR)/bin/activate
	$(PYTHON_BIN) -m py_compile $(BACKEND_DIR)/*.py
	@echo "Backend Python syntax check passed"

clean:
	rm -rf $(VENV_DIR)
	find . -type d -name '__pycache__' -print -exec rm -rf {} +
	find . -type f -name '*.pyc' -print -delete
	@echo "Cleaned virtualenv and Python cache files"