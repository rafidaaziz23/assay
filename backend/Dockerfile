# Assay — backend image for Google Cloud Run.
# Context MUST be the repo root: the backend imports the DEV 3 engine at repo-root
# ai/, and ai/catalog.py reads prompts/honeypot-catalog.json relative to that same
# root. Building with context=backend/ ships an image with no engine (the app then
# silently serves the deterministic fallback instead of Gemini).
FROM python:3.11-slim AS builder

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt ./backend/requirements.txt
RUN pip install --no-cache-dir --user -r backend/requirements.txt

FROM python:3.11-slim

WORKDIR /app

COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH
ENV PYTHONUNBUFFERED=1
ENV PORT=8080

# Backend app + the DEV 3 engine package it imports.
COPY backend/ ./backend/
COPY ai/ ./ai/
COPY prompts/ ./prompts/

RUN mkdir -p /app/data/uploads

EXPOSE 8080

WORKDIR /app/backend

# Cloud Run injects $PORT.
CMD exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT}
