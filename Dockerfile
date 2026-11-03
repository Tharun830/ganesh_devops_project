# ==============================================================================
# Ganesh DevOps Project - Production Dockerfile
# Multi-stage optimized, secure non-root container image
# ==============================================================================

FROM python:3.11-slim AS base

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    APP_HOME=/app \
    PORT=5000

WORKDIR ${APP_HOME}

# Install system dependencies (curl for container healthcheck)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies in a cached layer
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code
COPY app/ ./app/

# Create a non-privileged user and group for security
RUN groupadd -r devops && useradd -r -g devops -d ${APP_HOME} appuser \
    && chown -R appuser:devops ${APP_HOME}

# Switch to non-root user
USER appuser

# Expose web application port
EXPOSE 5000

# Docker native container healthcheck
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# Production WSGI server execution
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--access-logfile", "-", "app.main:app"]
