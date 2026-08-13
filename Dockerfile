# syntax=docker/dockerfile:1

FROM python:3.12-slim

WORKDIR /app

# Install build dependencies for packages that compile extensions
RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy packaging metadata and install the package
COPY pyproject.toml README.md ./
COPY src/ src/
COPY web/ web/
RUN pip install --no-cache-dir -e "."

# Create a non-root user and grant ownership of the working directory
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

# The Ollama host must be reachable from inside the container.
# Override with KWA_BASE_URL when running, e.g. host.docker.internal:11434.
ENV KWA_BASE_URL=http://host.docker.internal:11434

EXPOSE 8000

CMD ["python", "-m", "uvicorn", "kenya_wealth_agent.interfaces.web.app:app", "--host", "0.0.0.0", "--port", "8000"]
