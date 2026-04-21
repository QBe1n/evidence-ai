.PHONY: help dev test lint format type-check docker-up docker-down db-migrate db-reset clean install

# Directory containing this Makefile (repo root). Ensures alembic finds alembic.ini / alembic/.
ROOT := $(dir $(abspath $(lastword $(MAKEFILE_LIST))))

PYTHON := python
PYTEST := pytest
RUFF := ruff
MYPY := mypy

# Default target
help:
	@echo "EvidenceAI Development Commands"
	@echo "================================"
	@echo ""
	@echo "  make install      Install package in editable mode with dev dependencies"
	@echo "  make dev          Start FastAPI development server with hot reload"
	@echo "  make test         Run test suite with coverage"
	@echo "  make test-fast    Run tests (skip slow/integration/llm tests)"
	@echo "  make lint         Run ruff linter"
	@echo "  make format       Auto-format with ruff"
	@echo "  make type-check   Run mypy type checking"
	@echo "  make check        Run lint + type-check (CI equivalent)"
	@echo "  make docker-up    Start full stack (API + Redis + PostgreSQL)"
	@echo "  make docker-down  Stop Docker stack"
	@echo "  make db-migrate   Run Alembic database migrations"
	@echo "  make db-reset     Drop and recreate database (DESTRUCTIVE)"
	@echo "  make clean        Remove build artifacts and caches"
	@echo ""

# ── Installation ──────────────────────────────────────────────────────────────
install:
	pip install -e ".[dev]"

# ── Development server ────────────────────────────────────────────────────────
dev:
	uvicorn evidence_ai.main:app \
		--reload \
		--host 0.0.0.0 \
		--port 8000 \
		--log-level debug

dev-worker:
	celery -A evidence_ai.worker worker \
		--loglevel=info \
		--concurrency=4 \
		-Q evidence,default

# ── Testing ───────────────────────────────────────────────────────────────────
test:
	$(PYTEST) \
		--cov=evidence_ai \
		--cov-report=term-missing \
		--cov-report=html \
		-v

test-fast:
	$(PYTEST) \
		-m "not slow and not integration and not llm" \
		--cov=evidence_ai \
		--cov-report=term-missing \
		-v

test-integration:
	$(PYTEST) \
		-m "integration" \
		-v

# ── Code quality ──────────────────────────────────────────────────────────────
lint:
	$(RUFF) check src/ tests/

format:
	$(RUFF) format src/ tests/
	$(RUFF) check --fix src/ tests/

type-check:
	$(MYPY) src/evidence_ai/

check: lint type-check
	@echo "All checks passed."

# ── Docker ────────────────────────────────────────────────────────────────────
docker-up:
	docker compose up -d
	@echo "Services started. API available at http://localhost:8000"
	@echo "API docs: http://localhost:8000/docs"

docker-down:
	docker compose down

docker-build:
	docker compose build --no-cache

docker-logs:
	docker compose logs -f api

# ── Database ──────────────────────────────────────────────────────────────────
db-migrate:
	cd "$(ROOT)" && alembic upgrade head

db-downgrade:
	cd "$(ROOT)" && alembic downgrade -1

db-revision:
	cd "$(ROOT)" && alembic revision --autogenerate -m "$(MSG)"

db-reset:
	@echo "WARNING: This will destroy all data. Press Ctrl+C to abort."
	@sleep 3
	cd "$(ROOT)" && alembic downgrade base
	cd "$(ROOT)" && alembic upgrade head

# ── Utilities ─────────────────────────────────────────────────────────────────
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true
	rm -f .coverage coverage.xml

docs:
	mkdocs serve

docs-build:
	mkdocs build

.env:
	cp .env.example .env
	@echo ".env file created from .env.example. Please fill in your values."
