.PHONY: help install install-dev lint format type test test-cov clean cli web pre-commit

PYTHON := python3
VENV := .venv
PIP := $(VENV)/bin/pip
PYTHON_VENV := $(VENV)/bin/python

help:
	@echo "Available targets:"
	@echo "  install      Create venv and install runtime dependencies"
	@echo "  install-dev  Install package in editable mode with dev dependencies"
	@echo "  lint         Run ruff linter"
	@echo "  format       Run ruff formatter (check mode)"
	@echo "  format-fix   Run ruff formatter (write mode)"
	@echo "  type         Run mypy type checker"
	@echo "  test         Run pytest"
	@echo "  test-cov     Run pytest with coverage"
	@echo "  cli          Run the CLI"
	@echo "  web          Run the web UI"
	@echo "  pre-commit   Install and run pre-commit hooks"
	@echo "  clean        Remove build artifacts"

install:
	$(PYTHON) -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install -e .

install-dev:
	$(PYTHON) -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install -e ".[dev]"
	$(VENV)/bin/pre-commit install

lint:
	$(VENV)/bin/ruff check .

format:
	$(VENV)/bin/ruff format --check .

format-fix:
	$(VENV)/bin/ruff format .

type:
	$(VENV)/bin/mypy src/kenya_wealth_agent

test:
	$(VENV)/bin/pytest

test-cov:
	$(VENV)/bin/pytest --cov=kenya_wealth_agent --cov-report=term-missing --cov-report=html

pre-commit:
	$(VENV)/bin/pre-commit install
	$(VENV)/bin/pre-commit run --all-files

cli:
	$(PYTHON_VENV) -m kenya_wealth_agent.interfaces.cli.app

web:
	$(PYTHON_VENV) -m uvicorn kenya_wealth_agent.interfaces.web.app:app --host 127.0.0.1 --port 8000 --reload

clean:
	rm -rf build/ dist/ .eggs/ .mypy_cache/ .ruff_cache/ .pytest_cache/ htmlcov/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
