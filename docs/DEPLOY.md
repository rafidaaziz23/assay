# Deploy to Google Cloud Run

The event requires the live prototype on **Cloud Run or Firebase** with a public URL
(`01-event-guidelines/04-rules-eligibility.md` §3.2; localhost does not qualify).
Firebase Hosting's free tier only serves static files, so a Python backend must go to
**Cloud Run**.

One-shot script: `tools/deploy-cloudrun.sh`.

## Prerequisites (one-time)

1. **gcloud installed + logged in.**
   ```bash
   gcloud auth login
   ```
2. **A billing account in good standing.** Cloud Run refuses to deploy without one
   even though the free tier covers this workload (~$0/month). A closed or
   "not in good standing" account fails with `UREQ_PROJECT_BILLING_NOT_OPEN`.
   Create a fresh one at https://console.cloud.google.com/billing if needed.

## Deploy

From the **repo root**:

```bash
# first run — creates the Gemini secret too
GEMINI_KEY='<your-gemini-api-key>' BILLING='<billing-account-id>' \
  bash tools/deploy-cloudrun.sh

# later runs — secret already exists
bash tools/deploy-cloudrun.sh
```

The script: checks `ai/` imports → sets project + billing → enables APIs →
creates the Artifact Registry repo → stores the Gemini key in Secret Manager →
builds the image (context = repo root) → pushes → deploys → prints the live URL and
hits `/health`.

## Cost

Scale-to-zero (`--min-instances 0`), so idle cost is $0. A demo-level load (~1k
requests/month) sits far inside the free tier: 2M requests, 180k vCPU-s, 360k GiB-s.

| Item | Monthly |
|---|---|
| Cloud Run compute | $0 |
| Artifact Registry (image) | $0 – 0.05 |
| **Total** | **~$0 – 0.05** |

**Do not set `--min-instances 1`** — an always-on instance is ~$65/month.

## Why the build context is the repo root

`backend/Dockerfile` does `COPY backend/ ai/ prompts/`. The backend imports the DEV 3
engine at repo-root `ai/`, and `ai/catalog.py` reads
`prompts/honeypot-catalog.json` relative to that root. Building with
`context=backend/` ships an image with **no engine** — every request then silently
serves the deterministic fallback instead of Gemini, and `/health` still reports the
Gemini model. Always build from the root:

```bash
docker build -f backend/Dockerfile .
```

## Verify a deploy

```bash
URL=$(gcloud run services describe assay-backend --region asia-southeast2 --format='value(status.url)')
curl -sS "$URL/health"          # {"status":"healthy",...,"demo_mode":"live"}
curl -sS "$URL/api/v1/roles"    # 9 seed roles
```

If `demo_mode` reads `cached`, the `DEMO_MODE` env var or the Gemini secret is missing.

## Manual equivalent

```bash
gcloud config set project assay-aibc-2610152153
gcloud services enable run.googleapis.com artifactregistry.googleapis.com secretmanager.googleapis.com
gcloud artifacts repositories create assay --location=asia-southeast2 --repository-format=docker
gcloud auth configure-docker asia-southeast2-docker.pkg.dev
docker build -f backend/Dockerfile -t asia-southeast2-docker.pkg.dev/assay-aibc-2610152153/assay/assay-backend:latest .
docker push asia-southeast2-docker.pkg.dev/assay-aibc-2610152153/assay/assay-backend:latest
gcloud run deploy assay-backend --image asia-southeast2-docker.pkg.dev/assay-aibc-2610152153/assay/assay-backend:latest \
  --region asia-southeast2 --allow-unauthenticated --port 8080 \
  --memory 512Mi --cpu 1 --min-instances 0 --max-instances 3 \
  --set-env-vars DEMO_MODE=live \
  --set-secrets GOOGLE_API_KEY=assay-gemini-key:latest
```
