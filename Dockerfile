# Stage 1: Build the application
FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim AS builder

ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy

# Create app directory
WORKDIR /app

# Copy dependency files first for better layer caching
COPY pyproject.toml uv.lock ./

# Install dependencies only (no project code yet)
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-install-project --no-editable --no-dev

# Copy application source code
COPY . /app
COPY ./.git /app/.git

# Create README.md if not present (required by hatchling build)
RUN touch README.md

RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install the project itself
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-editable --no-dev

# Stage 2: Runtime image
FROM python:3.13-slim-bookworm AS runtime

# Install utilities for health checks
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    procps \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user for security
RUN groupadd --gid=1000 app \
    && useradd --uid=1000 --gid=app --shell=/bin/bash --create-home app

# Copy only the virtual environment and source code to the final image
COPY --from=builder --chown=app:app /app/.venv /app/.venv
COPY --from=builder --chown=app:app /app/src /app/src
COPY --from=builder --chown=app:app /app/pyproject.toml /app/pyproject.toml

# Set up environment
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH="/app/src"

# Switch to non-root user
USER app
WORKDIR /app

# Expose the MCP server port
EXPOSE 3000

# Default command to run MCP server on HTTP transport
# CMD ["fastmcp", "run", "mcp_server.py:mcp", "--transport", "http", "--port", "3000", "--host", "0.0.0.0"]
CMD ["uv", "run", "uvicorn", "pmv_rag1.main:app", "--host", "0.0.0.0", "--port", "8000"]
