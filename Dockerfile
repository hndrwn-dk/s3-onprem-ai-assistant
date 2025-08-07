# Dockerfile for S3 On-Premises AI Assistant v2.2.7
# Multi-stage build for optimal security and size

# Build stage
FROM python:3.11-slim as builder

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd --create-home --shell /bin/bash s3ai

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --user --no-warn-script-location -r requirements.txt

# Production stage
FROM python:3.11-slim as production

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/home/s3ai/.local/bin:$PATH" \
    S3AI_LOG_LEVEL=INFO \
    S3AI_API_HOST=0.0.0.0 \
    S3AI_API_PORT=8000

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create non-root user
RUN useradd --create-home --shell /bin/bash s3ai

# Set working directory
WORKDIR /app

# Copy Python packages from builder stage
COPY --from=builder /home/s3ai/.local /home/s3ai/.local

# Copy application code
COPY --chown=s3ai:s3ai . .

# Create necessary directories
RUN mkdir -p docs cache s3_all_docs \
    && chown -R s3ai:s3ai /app

# Switch to non-root user
USER s3ai

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${S3AI_API_PORT}/health || exit 1

# Expose port
EXPOSE 8000

# Default command
CMD ["python", "api.py"]