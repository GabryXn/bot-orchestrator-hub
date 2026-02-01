# =============================================================================
# MULTI-STAGE BUILD FOR PRODUCTION
# =============================================================================
# Stage 1: Build dependencies
FROM python:3.12-slim AS builder

WORKDIR /app

# Copy only requirements first for better caching
COPY requirements.txt .

# Install dependencies to a specific directory
RUN pip install --no-cache-dir --target=/app/deps -r requirements.txt

# =============================================================================
# Stage 2: Production image
# =============================================================================
FROM python:3.12-slim

# Security: Create non-root user with specific UID/GID
RUN groupadd -g 1001 appgroup && \
    useradd -u 1001 -g appgroup -s /bin/false appuser

WORKDIR /app

# Copy dependencies from builder stage
COPY --from=builder /app/deps /usr/local/lib/python3.12/site-packages

# Copy application code with proper ownership
COPY --chown=appuser:appgroup . .

# Switch to non-root user
USER appuser

# Environment variables
ENV PYTHONUNBUFFERED=True \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8080

# Expose Cloud Run default port
EXPOSE 8080

# Health check for container orchestration
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8080/health')" || exit 1

# Run with uvicorn (single worker for Cloud Run scaling)
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
