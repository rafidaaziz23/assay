#!/usr/bin/env bash
# Assay — one-shot Cloud Run deploy (AI Builder Cup 2026).
#
# The event requires the live prototype on Google Cloud Run or Firebase
# (04-rules-eligibility.md section 3.2). This script builds the backend image,
# pushes it to Artifact Registry, and deploys to Cloud Run with scale-to-zero so
# it stays inside the free tier (~$0/month).
#
# Prereqs (one-time):
#   1. A GCP billing account in good standing. Cloud Run refuses to deploy without
#      one even though usage is $0; a closed account fails with
#      UREQ_PROJECT_BILLING_NOT_OPEN.
#   2. gcloud installed and `gcloud auth login` done.
#
# Usage (from the repo root):
#   bash tools/deploy-cloudrun.sh
#   BILLING=01B687-... bash tools/deploy-cloudrun.sh
#   GEMINI_KEY=AQ.Ab8... bash tools/deploy-cloudrun.sh   # creates/updates the secret
#
# Re-runnable: safe after a code change (rebuilds + redeploys).

set -euo pipefail

# ---- config (override via env) ------------------------------------------------
PROJECT="${PROJECT:-assay-aibc-2610152153}"
REGION="${REGION:-asia-southeast2}"          # Jakarta
SERVICE="${SERVICE:-assay-backend}"
REPO="${REPO:-assay}"
BILLING="${BILLING:-}"
SECRET="${SECRET:-assay-gemini-key}"
GEMINI_KEY="${GEMINI_KEY:-}"
TAG="$(date +%Y%m%d-%H%M%S)"
IMAGE="${REGION}-docker.pkg.dev/${PROJECT}/${REPO}/${SERVICE}:${TAG}"

# ---- locate gcloud (its .cmd wrapper breaks under bash when the path has spaces)
if command -v gcloud >/dev/null 2>&1; then
  gc() { gcloud "$@"; }
else
  GS="${CLOUDSDK_ROOT:-$HOME/AppData/Local/Google/Cloud SDK/google-cloud-sdk}"
  if [ -x "$GS/platform/bundledpython/python.exe" ]; then
    gc() { "$GS/platform/bundledpython/python.exe" "$GS/lib/gcloud.py" "$@"; }
  else
    echo "gcloud not found. Install the Cloud SDK or set CLOUDSDK_ROOT." >&2
    exit 1
  fi
fi

say() { printf '\n== %s ==\n' "$*"; }

# ---- 0. sanity: engine must be importable from the repo root ------------------
say "check: engine importable (build context must be the repo root)"
PY_BIN="$(command -v python3 || command -v python || true)"
[ -x ".venv/Scripts/python.exe" ] && PY_BIN=".venv/Scripts/python.exe"
[ -x ".venv/bin/python" ] && PY_BIN=".venv/bin/python"
[ -n "$PY_BIN" ] && "$PY_BIN" -c "import ai" 2>/dev/null \
  || { echo "run from the repo root (ai/ must import)"; exit 1; }

# ---- 1. project + billing -----------------------------------------------------
say "project: $PROJECT"
gc config set project "$PROJECT"
[ -n "$BILLING" ] && gc billing projects link "$PROJECT" --billing-account="$BILLING"
if ! gc billing projects describe "$PROJECT" 2>/dev/null | grep -q "billingEnabled: true"; then
  echo "!! Billing is NOT enabled on $PROJECT."
  echo "   Create a billing account in good standing at https://console.cloud.google.com/billing"
  echo "   then re-run with BILLING=<account-id>."
  exit 1
fi

# ---- 2. APIs ------------------------------------------------------------------
say "enabling APIs (run, artifactregistry, secretmanager)"
gc services enable run.googleapis.com artifactregistry.googleapis.com secretmanager.googleapis.com

# ---- 3. Artifact Registry repo ------------------------------------------------
say "artifact registry repo: $REPO ($REGION)"
gc artifacts repositories describe "$REPO" --location="$REGION" >/dev/null 2>&1 \
  || gc artifacts repositories create "$REPO" --location="$REGION" \
       --repository-format=docker --description="Assay images"

# ---- 4. Gemini key in Secret Manager (never bake the key into the image) ------
say "secret: $SECRET"
if [ -n "$GEMINI_KEY" ]; then
  if gc secrets describe "$SECRET" >/dev/null 2>&1; then
    printf '%s' "$GEMINI_KEY" | gc secrets versions add "$SECRET" --data-file=-
  else
    printf '%s' "$GEMINI_KEY" | gc secrets create "$SECRET" --data-file=-
  fi
fi
if ! gc secrets describe "$SECRET" >/dev/null 2>&1; then
  echo "!! secret $SECRET missing. Re-run with GEMINI_KEY=<key> once."
  exit 1
fi

# ---- 5. build + push (context is the REPO ROOT; see backend/Dockerfile) -------
say "build + push: $IMAGE"
gc auth configure-docker "${REGION}-docker.pkg.dev" --quiet
docker build -f backend/Dockerfile -t "$IMAGE" .
docker push "$IMAGE"

# ---- 6. deploy (scale-to-zero => free tier) -----------------------------------
say "deploy: $SERVICE"
gc run deploy "$SERVICE" \
  --image "$IMAGE" \
  --region "$REGION" \
  --platform managed \
  --allow-unauthenticated \
  --port 8080 \
  --memory 512Mi \
  --cpu 1 \
  --min-instances 0 \
  --max-instances 3 \
  --set-env-vars "DEMO_MODE=live,GEMINI_MODEL=gemini-3-flash-preview,GEMINI_PRO_MODEL=gemini-3.1-pro-preview" \
  --set-secrets "GOOGLE_API_KEY=${SECRET}:latest"

# ---- 7. verify ----------------------------------------------------------------
URL="$(gc run services describe "$SERVICE" --region "$REGION" --format='value(status.url)')"
say "live: $URL"
echo "health:"; curl -sS "$URL/health"; echo
echo "roles :"; curl -sS "$URL/api/v1/roles" | head -c 200; echo
echo
echo "Deliverable URL for the submission: $URL"
