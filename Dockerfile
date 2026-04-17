# ── Stage 1: Python dependencies ──────────────────────────────────────────────
FROM python:3.11-slim AS builder

WORKDIR /build

# Install build tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency files
COPY pyproject.toml README.md ./
COPY src/ src/

# Build wheel
RUN pip install --upgrade pip hatchling && \
    pip wheel --no-cache-dir --wheel-dir /wheels -e ".[all]" 2>/dev/null || \
    pip wheel --no-cache-dir --wheel-dir /wheels .

# Install into /install prefix
RUN pip install --no-cache-dir --prefix=/install \
    fastapi uvicorn[standard] pydantic pydantic-settings \
    sqlalchemy[asyncio] asyncpg alembic \
    httpx tenacity \
    celery[redis] redis \
    openai anthropic tiktoken \
    transformers torch numpy scipy scikit-learn pandas \
    lxml beautifulsoup4 biopython \
    jinja2 markdown reportlab python-docx \
    python-jose[cryptography] passlib[bcrypt] \
    click rich python-dateutil pytz

# ── Stage 2: Runtime image ────────────────────────────────────────────────────
FROM python:3.11-slim AS runtime

# Security: run as non-root user
RUN groupadd -r evidence && useradd -r -g evidence evidence

WORKDIR /app

# Runtime dependencies only
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy installed packages from builder
COPY --from=builder /install /usr/local

# Copy application source
COPY src/ src/
COPY alembic.ini ./
COPY alembic/ alembic/ 2>/dev/null || true

# Copy entrypoint scripts
COPY scripts/ scripts/ 2>/dev/null || true

# Set ownership
RUN chown -R evidence:evidence /app

USER evidence

# Expose API port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Default command: start FastAPI server
CMD ["uvicorn", "evidence_ai.main:app", \
     "--host", "0.0.0.0", \
     "--port", "8000", \
     "--workers", "4", \
     "--proxy-headers", \
     "--forwarded-allow-ips", "*"]

# ── Stage 3: Worker image (Celery) ────────────────────────────────────────────
FROM runtime AS worker

CMD ["celery", "-A", "evidence_ai.worker", "worker", \
     "--loglevel=info", \
     "--concurrency=4", \
     "-Q", "evidence,default"]
