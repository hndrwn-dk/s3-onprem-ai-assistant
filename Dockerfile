# syntax=docker/dockerfile:1

FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install system deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    pkg-config \
    libssl-dev \
    libffi-dev \
    rustc \
    cargo \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements and install
COPY requirements.txt ./
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt

# Copy app code
COPY . .

# Create required dirs
RUN mkdir -p cache s3_all_docs docs

EXPOSE 8000

ENV MODEL=phi3:mini \
    VECTOR_SEARCH_K=3 \
    CACHE_TTL_HOURS=24

CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]