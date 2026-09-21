# Production Dockerfile for Recruitment Pro FastAPI Backend on Render
FROM python:3.12-slim

# Prevent Python from writing .pyc files and enable unbuffered logging
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install system dependencies for PostgreSQL and compilation
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install python packages
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy backend application source code
COPY . .

# Render exposes dynamic PORT environment variable (default: 8000)
EXPOSE 8000

# Execute PostgreSQL schema initializer & launch Uvicorn server
CMD sh -c "python init_postgres.py && uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"
