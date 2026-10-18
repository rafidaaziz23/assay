# Assay — frontend image for Google Cloud Run.
# Context MUST be the repo root: `docker build -f frontend/Dockerfile .`
#
# The API base is baked as a relative path ("/api/v1") so the image is portable across
# environments; nginx proxies /api to the backend service named by $BACKEND_URL at
# container start. That also removes CORS from the picture — the browser only ever
# talks to one origin.
FROM node:20-slim AS builder

WORKDIR /app

COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci

COPY frontend/ ./

# "cached" pins every API call to the deterministic fixture set (Gemini never runs).
# "live" is the submission default: real Gemini, per-request mock fallback intact.
ARG VITE_DEMO_MODE=live
ENV VITE_API_BASE_URL=/api/v1 \
    VITE_USE_MOCK=false \
    VITE_DEMO_MODE=${VITE_DEMO_MODE}

# tsc runs as part of `npm run build`; a type error fails the image on purpose.
RUN npm run build

FROM nginx:1.27-alpine

COPY frontend/nginx.conf.template /etc/nginx/templates/default.conf.template
COPY --from=builder /app/dist /usr/share/nginx/html

# Cloud Run injects $PORT (default 8080). nginx's entrypoint runs envsubst over the
# template, so PORT and BACKEND_URL are both resolved at start.
ENV PORT=8080
ENV BACKEND_URL=http://127.0.0.1:8000

EXPOSE 8080
