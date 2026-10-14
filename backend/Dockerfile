# Multi-stage Dockerfile for Assay Backend on Google Cloud Run
FROM python:3.11-slim AS builder

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

FROM python:3.11-slim

WORKDIR /app

# Copy dependencies from builder
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH
ENV PYTHONUNBUFFERED=1
ENV PORT=8080

# Copy application source
COPY . .

# Create directory for uploads if needed
RUN mkdir -p /app/data/uploads

EXPOSE 8080

# Cloud Run injects $PORT environment variable
CMD exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT}
