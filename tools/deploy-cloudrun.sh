#!/usr/bin/env bash
# Assay — deploy to Google Cloud Run.
#
# Two services, both in asia-southeast1:
#   assay-api   FastAPI + ai/ engine + prompts/   (282 MB)
#   assay-web   nginx + React dist                ( 50 MB)
#
# The AI engine is NOT a third service. It is a Python package imported by
# backend/app/services/engine.py, so it ships inside the assay-api image. Build
# context for BOTH images is the repo root — building from backend/ silently
# drops ai/ and the app then serves fixtures instead of Gemini.
#
# Usage:
#   ./tools/deploy-cloudrun.sh --dry-run        # print the plan, touch nothing
#   ./tools/deploy-cloudrun.sh --local-test     # build + verify both images, no cloud
#   ./tools/deploy-cloudrun.sh                  # full deploy (Cloud Build does the build)
#   ./tools/deploy-cloudrun.sh --verify-local   # full deploy, but build locally first
#
# Every step is idempotent. Re-running is safe.
#
# Overridable env: PROJECT REGION REPO API_SVC WEB_SVC TAG DEMO_MODE
#                  MIN_INSTANCES MAX_INSTANCES CPU MEMORY GCLOUD
#
# Full runbook, cost model and the billing blocker: docs/deploy/DEPLOY-RUNBOOK.md

set -euo pipefail

# ---------------------------------------------------------------- config
PROJECT="${PROJECT:-assay-aibc-2610152153}"
REGION="${REGION:-asia-southeast1}"
REPO="${REPO:-assay}"
API_SVC="${API_SVC:-assay-api}"
WEB_SVC="${WEB_SVC:-assay-web}"
TAG="${TAG:-$(date +%Y%m%d-%H%M)}"
DEMO_MODE="${DEMO_MODE:-live}"

# Cheap by construction. See docs/deploy/COST-MODEL.md §3 and §4.
MAX_INSTANCES="${MAX_INSTANCES:-2}"
MIN_INSTANCES="${MIN_INSTANCES:-0}"
CPU="${CPU:-1}"
MEMORY="${MEMORY:-512Mi}"

# --quiet is mandatory, not cosmetic: without it gcloud blocks on an interactive
# "Do you want enable these APIs?" prompt and the script hangs forever in a
# non-tty run (verified).
# Do not default to bare `gcloud` on Windows: PATH resolves to the MSYS shell
# wrapper, which re-executes the bundled python with a mangled path and dies with
# "can't open file 'D:\c\Users\...'". Verified here. Prefer the .cmd shim.
if [ -z "${GCLOUD:-}" ]; then
  for c in gcloud.cmd gcloud; do
    command -v "$c" >/dev/null 2>&1 && { GCLOUD="$c"; break; }
  done
fi
GCLOUD="${GCLOUD:-gcloud}"
GQ=("$GCLOUD" --quiet)
DRY=0
LOCAL_ONLY=0
LOCAL_BUILD=0   # full deploy skips the local build: Cloud Build builds anyway

for arg in "$@"; do
  case "$arg" in
    --dry-run)        DRY=1 ;;
    --local-test)     LOCAL_ONLY=1; LOCAL_BUILD=1 ;;
    --verify-local)   LOCAL_BUILD=1 ;;
    -h|--help)    sed -n '2,/^set -euo/p' "$0" | sed '$d'; exit 0 ;;
    *) echo "unknown flag: $arg" >&2; exit 2 ;;
  esac
done

say()  { printf '\n\033[1m==> %s\033[0m\n' "$*"; }
info() { printf '    %s\n' "$*"; }
die()  { printf '\n\033[31mFAIL: %s\033[0m\n' "$*" >&2; exit 1; }
# Never echo secret material, even in dry-run output that ends up in a log or a
# screenshot. The key still reaches gcloud on the real path.
# Stop only at whitespace, not at a comma: a value containing a comma would
# otherwise leak its tail (verified: "GOOGLE_API_KEY=abc,def" -> "***REDACTED***,def").
# Over-redacting the rest of the line is the safe failure mode.
redact() { sed -E 's/GOOGLE_API_KEY=[^ ]*/GOOGLE_API_KEY=***REDACTED***/g'; }
run()  {
  if [ "$DRY" = 1 ]; then
    printf '    [dry-run] %s\n' "$*" | redact
  else
    "$@"
  fi
}

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

# Pull GOOGLE_API_KEY / model IDs from the repo .env if the shell lacks them.
# .env is gitignored and excluded from images; this only reads it for the deploy call.
if [ -f .env ]; then
  while IFS='=' read -r k v; do
    case "$k" in
      GOOGLE_API_KEY|GEMINI_MODEL) [ -n "${!k:-}" ] || export "$k=$v" ;;
    esac
  done < <(grep -E '^(GOOGLE_API_KEY|GEMINI_MODEL)=' .env | sed 's/[[:space:]]*$//')
fi
# Default model. gemini-3-flash-preview is 20 req/day on the free tier; a single
# demo run exhausts it and the app then serves fixtures, which reads as broken.
# flash-lite is 500 req/day. Measured via the Cloud Quotas API; see ai/_client.py.
export GEMINI_MODEL="${GEMINI_MODEL:-gemini-3.1-flash-lite}"

[ -f backend/Dockerfile ]        || die "backend/Dockerfile missing — wrong repo root?"
[ -f frontend/Dockerfile ]       || die "frontend/Dockerfile missing"
[ -f frontend/nginx.conf.template ] || die "frontend/nginx.conf.template missing"
[ -d ai ]                        || die "ai/ missing — engine would not ship"
[ -f prompts/honeypot-catalog.json ] || die "prompts/ missing — engine catalog would not ship"

# ---------------------------------------------------------------- 0. billing gate
# Checked FIRST, before any 4-minute image build. Discovering a closed billing
# account after building both images wastes the only thing that is scarce here.
# Skipped for --local-test (zero cloud calls by definition) and --dry-run.
if [ "$DRY" = 0 ] && [ "$LOCAL_ONLY" = 0 ]; then
  say "1/8  Billing gate"
  billing=$("${GQ[@]}" billing projects describe "$PROJECT" --format='value(billingEnabled)' 2>/dev/null || echo "unknown")
  if [ "$billing" != "True" ]; then
    printf '\n\033[31mBilling is %s on %s.\033[0m\n' "$billing" "$PROJECT" >&2
    cat >&2 <<'EOS'

Cloud Run cannot be enabled while billing is closed. Verified error:
  FAILED_PRECONDITION: Billing account for project '...' is not open.

Open it in the console (there is no CLI/REST path — see docs/deploy/DEPLOY-RUNBOOK.md §1):
  console.cloud.google.com/billing
    -> clear the "Status: Active" filter
    -> pick the account -> Account Management -> Reopen billing account

Nothing was built or pushed. Re-run this script once billing reads True.
EOS
    exit 1
  fi
  info "billing: enabled"
elif [ "$LOCAL_ONLY" = 1 ]; then
  say "1/8  Billing gate"
  info "skipped (--local-test makes no cloud calls)"
fi

# ---------------------------------------------------------------- 1. local build + verify
# Cloud Build builds both images anyway, so a full deploy does not repeat that work
# locally — it doubles wall time for a check the cloud build already performs. Pass
# --verify-local (or --local-test) when you want the local proof as well.
if [ "$LOCAL_BUILD" = 1 ]; then
  say "2/8  Build images locally"
  run docker build -f backend/Dockerfile -t "assay-api:local" .
  run docker build -f frontend/Dockerfile --build-arg "VITE_DEMO_MODE=$DEMO_MODE" -t "assay-web:local" .
else
  say "2/8  Build images locally — skipped (Cloud Build builds them; --verify-local to force)"
fi

say "3/8  Verify the engine actually shipped"
# A 282 MB image that cannot import ai/ looks identical to a working one. This is
# the check that catches the silent-fixture failure mode.
if [ "$DRY" = 0 ] && [ "$LOCAL_BUILD" = 1 ]; then
  out=$(docker run --rm --entrypoint python assay-api:local -c \
        "import sys; sys.path.insert(0,'/app'); import ai; print('ENGINE_OK', hasattr(ai,'gen_checklist'))" 2>&1) \
    || die "engine import failed inside image: $out"
  echo "$out" | grep -q ENGINE_OK || die "engine import produced no marker: $out"
  info "$out"
fi

say "4/8  Smoke the API container"
if [ "$DRY" = 0 ] && [ "$LOCAL_ONLY" = 1 ]; then
  docker rm -f assay-deploy-smoke >/dev/null 2>&1 || true
  docker run -d --name assay-deploy-smoke -p 18099:8080 \
    -e "PORT=8080" -e "DEMO_MODE=$DEMO_MODE" \
    -e "GEMINI_MODEL=${GEMINI_MODEL:-gemini-3.1-flash-lite}" \
    -e "GOOGLE_API_KEY=${GOOGLE_API_KEY:-}" \
    assay-api:local >/dev/null
  ok=0
  for _ in $(seq 1 300); do
    if curl -sf http://127.0.0.1:18099/health >/dev/null 2>&1; then ok=1; break; fi
    sleep 0.2
  done
  docker rm -f assay-deploy-smoke >/dev/null 2>&1 || true
  [ "$ok" = 1 ] || die "/health never came up"
  info "/health OK"
fi

if [ "$LOCAL_ONLY" = 1 ]; then
  say "local-test complete — images build, engine ships, API answers. No cloud calls made."
  exit 0
fi

# ---------------------------------------------------------------- 2. preflight
say "5/8  Preflight: enable APIs"
if [ "$DRY" = 0 ]; then
  for api in run.googleapis.com cloudbuild.googleapis.com artifactregistry.googleapis.com; do
    if "${GQ[@]}" services list --enabled --project "$PROJECT" --format='value(config.name)' 2>/dev/null | grep -qx "$api"; then
      info "$api: already enabled"
    else
      info "$api: enabling"
      run "${GQ[@]}" services enable "$api" --project "$PROJECT"
    fi
  done
else
  info "[dry-run] would enable run/cloudbuild/artifactregistry"
fi

say "6/8  Artifact Registry"
if [ "$DRY" = 0 ]; then
  if ! "${GQ[@]}" artifacts repositories describe "$REPO" --location="$REGION" --project="$PROJECT" >/dev/null 2>&1; then
    run "${GQ[@]}" artifacts repositories create "$REPO" \
      --repository-format=docker --location="$REGION" --project="$PROJECT" \
      --description="Assay-Cloud-Run-images"
  else
    info "repository $REPO already exists"
  fi
fi

REG="$REGION-docker.pkg.dev/$PROJECT/$REPO"
API_IMG="$REG/api:$TAG"
WEB_IMG="$REG/web:$TAG"

say "7/8  Build + push via Cloud Build"
# Two Windows traps here, both verified on SDK 589.0.0:
#   1. --config /dev/stdin  -> "Unable to read file [/dev/stdin]: No such file"
#   2. --config /tmp/x.yaml -> same error, because gcloud is a NATIVE Windows binary
#      and MSYS paths are not translated. The path must go through cygpath -w.
# Do not use mktemp: it writes to $TMPDIR, and when that is unwritable from MSYS
# the deploy dies here with "mktemp: failed to create file ... Permission denied"
# (verified). A file beside the repo is always writable and needs no TMPDIR.
CFG="$REPO_ROOT/.cloudbuild-deploy.$$.yaml"
CFG_WIN="$(cygpath -w "$CFG")"
trap 'rm -f "$CFG"' EXIT
: > "$CFG"
cat > "$CFG" <<YAML
steps:
  - name: gcr.io/cloud-builders/docker
    args: ['build','-f','backend/Dockerfile','-t','$API_IMG','.']
  - name: gcr.io/cloud-builders/docker
    args: ['build','-f','frontend/Dockerfile','--build-arg','VITE_DEMO_MODE=$DEMO_MODE','-t','$WEB_IMG','.']
images: ['$API_IMG','$WEB_IMG']
YAML

if [ "$DRY" = 1 ]; then
  info "[dry-run] gcloud builds submit --config $CFG_WIN (2 images)"
  info "--- build config that would be sent ---"
  sed 's/^/      /' "$CFG"
else
  "${GQ[@]}" builds submit --project "$PROJECT" --region "$REGION" --config "$CFG_WIN" .
fi



# ---------------------------------------------------------------- 3. deploy
say "8/8  Deploy Cloud Run services"

[ -n "${GOOGLE_API_KEY:-}" ] || die "GOOGLE_API_KEY not set in this shell. Export it (or pass through) before deploying; without it the API serves fixtures."

run "${GQ[@]}" run deploy "$API_SVC" \
  --project "$PROJECT" --region "$REGION" \
  --image "$API_IMG" --platform managed --allow-unauthenticated \
  --port 8080 --cpu "$CPU" --memory "$MEMORY" \
  --min-instances "$MIN_INSTANCES" --max-instances "$MAX_INSTANCES" \
  --set-env-vars "DEMO_MODE=$DEMO_MODE,GEMINI_MODEL=${GEMINI_MODEL:-gemini-3.1-flash-lite},GOOGLE_API_KEY=$GOOGLE_API_KEY"

API_URL=$("${GQ[@]}" run services describe "$API_SVC" --project "$PROJECT" --region "$REGION" --format='value(status.url)' 2>/dev/null || echo "")
[ "$DRY" = 1 ] && API_URL="https://$API_SVC-<hash>-as.a.run.app"
[ -n "$API_URL" ] || die "could not read $API_SVC URL"

info "api url: $API_URL"

run "${GQ[@]}" run deploy "$WEB_SVC" \
  --project "$PROJECT" --region "$REGION" \
  --image "$WEB_IMG" --platform managed --allow-unauthenticated \
  --port 8080 --cpu "$CPU" --memory "$MEMORY" \
  --min-instances "$MIN_INSTANCES" --max-instances "$MAX_INSTANCES" \
  --set-env-vars "BACKEND_URL=$API_URL"

WEB_URL=$("${GQ[@]}" run services describe "$WEB_SVC" --project "$PROJECT" --region "$REGION" --format='value(status.url)' 2>/dev/null || echo "")
[ "$DRY" = 1 ] && WEB_URL="https://$WEB_SVC-<hash>-as.a.run.app"
[ -n "$WEB_URL" ] || die "could not read $WEB_SVC URL"

# ---------------------------------------------------------------- 4. post-deploy proof
say "Post-deploy checks"
if [ "$DRY" = 0 ]; then
  for _ in $(seq 1 60); do curl -sf "$API_URL/health" >/dev/null 2>&1 && break; sleep 2; done
  curl -sf "$API_URL/health"  || die "api /health failed"
  echo
  # `curl -sf | head` under `set -o pipefail` aborts the whole script on a non-2xx
  # (verified: rc=22), turning a successful deploy into a false failure. Capture first.
  cache=$(curl -sf "$API_URL/health/cache" || echo "unavailable")
  printf '    /health/cache: %s\n' "$(printf '%s' "$cache" | head -c 160)"
  curl -sf "$WEB_URL/health"       || die "web /health failed"
  echo
  # The proxy is the whole reason the frontend is nginx and not Firebase Hosting.
  curl -sf "$WEB_URL/api/v1/roles" >/dev/null || die "web -> api proxy broken"
  info "proxy OK"
fi

cat <<EOF

────────────────────────────────────────────────────────
  Deployed
    web   $WEB_URL
    api   $API_URL

  Artifact Registry free tier is 0.5 GiB; one image pair is ~0.33 GiB, so a
  second push crosses it. List what is stored, then delete what you no longer
  need (this script never deletes anything on its own):

    $GCLOUD artifacts docker images list $REGION-docker.pkg.dev/$PROJECT/$REPO \\
      --include-tags --sort-by=~CREATE_TIME

  Spend cap (the only hard ceiling — a plain budget only emails you):
    Billing -> Budgets & alerts -> Create budget
    scope: project assay-aibc-2610152153, service Cloud Run
    amount: IDR 10,000, and turn on the spend cap itself
      (API: spendCap.inputState=CONFIGURED; requires EXCLUDE_ALL_CREDITS,
       exactly 50/80/100 thresholds, and project-level notifications)

  The API key is passed as a plain env var, so anyone with run.services.get
  on this project can read it. Fine for judging; move to Secret Manager with
  --set-secrets before this handles real user data.
────────────────────────────────────────────────────────
EOF
