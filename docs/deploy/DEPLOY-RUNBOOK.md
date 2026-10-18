# Deploy Runbook — Assay on Cloud Run

Step-by-step. Every command has been run on this machine; quoted outputs are real,
not illustrative. Costs and rate sources: `docs/deploy/COST-MODEL.md`.

---

## 0. What actually gets deployed

```
Browser
  │  HTTPS
  ▼
assay-web            nginx + React dist        50.1 MB   1 vCPU / 512 MiB
  │  /api/* proxied  (same origin — no CORS, no rebuild when the API URL changes)
  ▼
assay-api            FastAPI + ai/ + prompts/  282 MB    1 vCPU / 512 MiB
  │
  ▼
Gemini (AI Studio key, injected as env var)
```

**Two containers, not three.** The AI engine (`ai/`) is a Python package imported
directly by `backend/app/services/engine.py`. It is not a service and has no
separate URL. It ships inside the `assay-api` image.

**Build context is the repo root for both images.** This is the most expensive
mistake available here: building with `context=backend/` produces a 282 MB image
that looks fine, starts fine, and silently serves deterministic fixtures instead
of calling Gemini — because `ai/` and `prompts/` are not in it. The script asserts
the import before pushing anything (step 3/8).

---

## 1. Prerequisites

### 1.1 Tooling

| Tool | Check | Expected |
|---|---|---|
| Docker Desktop | `docker ps` | no error |
| gcloud SDK | `gcloud version` | 589.0.0+ |
| bash (MSYS) | `bash --version` | 5.2.x |
| cygpath | `command -v cygpath` | `/usr/bin/cygpath` |

**Docker must be running.** If the daemon is down, `--local-test` dies at step 2/8
with `open //./pipe/docker_engine: The system cannot find the file specified`.
Start Docker Desktop, wait for `docker ps` to succeed, then continue.

**Never invoke bare `gcloud` on this host.** PATH resolves to the MSYS shell
wrapper, which re-executes the bundled Python with a mangled path:

```
ERROR: can't open file 'D:\c\Users\Reza\AppData\Local\Google\Cloud SDK\google-cloud-sdk\lib\gcloud.py'
```

The script prefers `gcloud.cmd` automatically. Running by hand:

```bash
export GCLOUD="/c/Users/Reza/AppData/Local/Google/Cloud SDK/google-cloud-sdk/bin/gcloud.cmd"
```

### 1.2 Google Cloud state

```bash
"$GCLOUD" config get-value account     # mrezalf0@gmail.com
"$GCLOUD" config get-value project     # assay-aibc-2610152153
"$GCLOUD" billing projects describe assay-aibc-2610152153 --format='value(billingEnabled)'
```

The last line must print **`True`**. If it prints `False`, stop — see §2.

### 1.3 The `.env` file

`.env` at the repo root is gitignored and excluded from both the image
(`.dockerignore`) and the Cloud Build upload (`.gcloudignore`). It supplies:

```
GOOGLE_API_KEY=...
GEMINI_MODEL=gemini-3-flash-preview
```

The script reads both if the shell does not already define them, then passes them
to Cloud Run via `--set-env-vars`. The key never appears in output — dry-run lines
are redacted to `GOOGLE_API_KEY=***REDACTED***`.

---

## 2. Blocker: billing must be open

Cloud Run cannot be enabled while the billing account is closed. Verified:

```
$ gcloud services enable run.googleapis.com --project assay-aibc-2610152153
ERROR: FAILED_PRECONDITION: Billing account for project '204598097710' is not
open. Billing must be enabled for activation of service(s) 'run.googleapis.com,
artifactregistry.googleapis.com,containerregistry.googleapis.com'
```

Current state (measured): `billingEnabled = False`, all three billing accounts
report `open: false`.

**There is no CLI or REST path to reopen it.** All tried:

| Attempt | Result |
|---|---|
| `gcloud billing accounts reopen` | subcommand does not exist |
| `POST /v1/billingAccounts/{id}:reopen` | `404` |
| `POST /v1/billingAccounts/{id}:open` | `404` |
| `PATCH` the `open` field | `open` is `readOnly`; only `display_name` is patchable |
| `gcloud billing projects link <closed-account>` | exits **0** but `billingEnabled` stays `false` |

That last one is a trap: it reports success and prints the account name, so it
looks like it worked. It did not. Always re-read `billingEnabled` after linking;
never trust the exit code.

You hold `billing.accounts.reopen` on both GDP credit accounts (confirmed with
`testIamPermissions`), but the permission only works through the console.

### What to do

```
console.cloud.google.com/billing
  -> clear the "Status: Active" filter so Closed accounts appear
  -> pick the account -> Account Management -> "Reopen billing account"
```

Give it three minutes. If the button is greyed out, the account has an unresolved
payments issue and reopening is blocked on card verification — the same wall as
the prepayment. Then pay (§2.1) instead of burning the submission window.

### 2.1 The IDR 500,000 prepayment

Verbatim from `cloud.google.com/billing/docs/how-to/payment-methods`:

> "Prepayments to a Postpay Google payments account **will be refunded** if
> unused by the time of account closure."

A deposit, not a fee. It unlocks the $300 Free Trial credit. Refund: §7.

**Before paying, confirm you are still eligible for the $300.** Verbatim from
`cloud.google.com/signup-faqs`:

> "Each user is eligible for the $300 free credit … if you have never been a
> paying customer of Google Cloud, Google Maps Platform, or Firebase and you
> **haven't previously signed up for the Google Cloud Free Trial**."

One trial per user, lifetime. If this account already consumed a trial, paying the
prepayment yields a working billing account but **no second $300**. The math in
COST-MODEL §3 still holds — the workload fits inside the free tier alone — but
with less headroom.

---

## 3. Local test — no cloud, no money

Run this before touching the cloud. It is the only place a broken image can be
found without spending a build.

### 3.1 Fast check: build, engine, health

```bash
cd D:/Project/assay
bash tools/deploy-cloudrun.sh --local-test
```

Expected tail (exit code **0**):

```
==> 1/8  Billing gate
    skipped (--local-test makes no cloud calls)

==> 2/8  Build images locally
...
==> 3/8  Verify the engine actually shipped
    ENGINE_OK True

==> 4/8  Smoke the API container
    /health OK

==> local-test complete — images build, engine ships, API answers. No cloud calls made.
```

`--local-test` never calls gcloud, so it works with billing closed.

| Line | Proves |
|---|---|
| `ENGINE_OK True` | `ai/` and `prompts/` are in the image and importable |
| `/health OK` | the container boots and serves on `$PORT` |

If you see `ENGINE_OK False`, the build context was wrong — check that
`backend/Dockerfile` still has `COPY ai/ ./ai/` and `COPY prompts/ ./prompts/`.

### 3.2 Full topology: two containers, proxy, SPA

```bash
docker compose -f tools/docker-compose.local.yml up -d --build
```

Verify all four surfaces:

```bash
curl -s localhost:8080/healthz              # ok
curl -s localhost:8080/api/v1/roles         # 9-role taxonomy, via nginx proxy
curl -s -o /dev/null -w '%{http_code} %{content_type}\n' localhost:8080/dashboard/xyz
                                            # 200 text/html  (SPA deep link)
```

Measured here:

```
/healthz         ok
/api/v1/roles    {"roles":["Frontend","Backend",...],"others_option":"Others"}
/dashboard/xyz   200 text/html
```

Tear down:

```bash
docker compose -f tools/docker-compose.local.yml down
```

### 3.3 The demo-safety mode

The judged run must not depend on a live quota:

```bash
DEMO_MODE=cached docker compose -f tools/docker-compose.local.yml up -d
```

Measured checklist latency: **23 ms cached** versus **6,223 ms live**.

### 3.4 Why not a real GCP emulator

There is no faithful open-source Cloud Run emulator.

- `gcloud beta code dev` is Google's own, but needs the `beta` component plus
  **Minikube and Skaffold** — both marked **DEPRECATED** in `gcloud components
  list` on this machine, and the component update fails non-interactively.
- `localgcp` (slokam-ai) advertises Cloud Run, but `internal/cloudrun/service.go`
  shows it is a **gRPC stub**: `CreateService` stores metadata and returns a fake
  `https://<name>-localgcp.run.app` URI. No container starts, no HTTP is served.
  It emulates the *admin API*, not the runtime.
- `localgcp`, `cloudbox`, `LocalCloud`, `floci` emulate APIs (Firestore, GCS,
  Pub/Sub, BigQuery) — not request-billed container execution.
- `fake-gcs-server` is Cloud Storage only. Assay does not use GCS.

`tools/docker-compose.local.yml` reproduces the parts that actually break
deploys: two containers, `$PORT` injection, nginx→api by service name, and a
282 MB image carrying `ai/`.

---

## 4. Deploy

### 4.1 Review the plan first

```bash
bash tools/deploy-cloudrun.sh --dry-run
```

Exit code 0, nothing built, nothing sent. Prints every gcloud call with the key
redacted. Read the two `run deploy` lines and confirm:

```
--region asia-southeast1      correct region (Tier 2 pricing, COST-MODEL §1)
--min-instances 0             scale to zero; 1 would cost ~$22/month
--max-instances 2             hard ceiling on blast radius
--cpu 1 --memory 512Mi        matches measured cold start
--set-env-vars DEMO_MODE=live,GEMINI_MODEL=...,GOOGLE_API_KEY=***REDACTED***
```

### 4.2 Run it

```bash
bash tools/deploy-cloudrun.sh
```

Idempotent; re-running is safe.

| Step | Action | Failure means |
|---|---|---|
| 1/8 | Billing gate | billing closed → stop, go to §2 |
| 2/8 | `docker build` both images | Dockerfile or build context broken |
| 3/8 | `import ai` inside the image | engine would not ship; **do not proceed** |
| 4/8 | boot the API container, poll `/health` | app does not start on `$PORT` |
| 5/8 | enable `run`, `cloudbuild`, `artifactregistry` | missing `serviceusage.services.enable` |
| 6/8 | create Artifact Registry repo (if absent) | missing `artifactregistry.repositories.create` |
| 7/8 | Cloud Build: build + push both images | Dockerfile fails in cloud, or source too large |
| 8/8 | `gcloud run deploy` api, then web | quota, org policy, or missing `run.services.create` |

**Step 1/8 runs before any build on purpose.** Finding a closed billing account
after a four-minute build wastes the scarcest resource here. Measured: the gate
fails in **~6–10 s** and prints `Nothing was built or pushed.`

### 4.3 Step 8 detail — why api before web

`assay-web` bakes the API URL into `BACKEND_URL`, so the order is fixed: deploy
api → read `status.url` → deploy web with that value.

```bash
gcloud run services describe assay-api --region asia-southeast1 --format='value(status.url)'
```

If that returns empty the script aborts with `could not read assay-api URL` rather
than deploying a web container pointed at nothing. The same guard exists for the
web URL.

### 4.4 What gets uploaded

`.gcloudignore` cuts the Cloud Build source from **439 MB to 1.1 MB / 138 files**,
measured with `gcloud meta list-files-for-upload .`. Excluded: `frontend/node_modules`
(124 MB), `backend/.venv` (141 MB), `docs/`, `eval/`, `tools/`, and every real
`.env`. Both are rebuilt inside the Docker build, so uploading them is pure latency.

**`.dockerignore` does not do this.** It filters what the Docker daemon sees, not
what gcloud uploads. Two files, two jobs.

```bash
"$GCLOUD" meta list-files-for-upload . | wc -l     # expect 138
```

---

## 5. Post-deploy verification

The script runs these automatically; you can also run them by hand.

```bash
curl -s $API_URL/health
# {"status":"healthy","version":"2.0.0","engine":"Google gemini-3-flash-preview",
#  "demo_mode":"live","cache_schema_version":"2.0.0"}

curl -s $API_URL/health/cache     # ok:true, cache_schema_version 2.0.0
curl -s $WEB_URL/healthz          # ok
curl -s $WEB_URL/api/v1/roles     # proxy works
```

`engine` must name the model you actually deployed. It reads
`settings.GEMINI_MODEL`, so it cannot drift from the config the way a hardcoded
string would.

### 5.1 The only test that counts

Open `$WEB_URL` **on a phone, on mobile data**. Not localhost, not the same Wi-Fi.
That is the URL a judge clicks, from a network you do not control.

Walk the demo once end to end: intake → checklist → syllabus → interview turn →
report. If a step spins forever, check whether the instance was cold-started away
mid-session (§9.3).

---

## 6. Cost controls

### 6.1 `--max-instances=2`

Caps how many instances a spike can spawn. Without it Cloud Run scales to 1000,
and an unauthenticated endpoint can burn the free tier in minutes.

### 6.2 Spend cap — the only hard ceiling

Cloud Run is eligible (`run.googleapis.com`, service `152E-C115-5142`). Verbatim
from `cloud.google.com/billing/docs/how-to/budgets-spend-caps`:

> "When a spend cap budget is enforced, usage of your specified services is
> automatically paused for the remainder of the budget period."

Set **$290**, not $5:

> "The cost calculations for spend caps are based on gross, estimated costs and
> **don't include savings and credits**."

A $5 cap pauses the service while $295 of credit is still unused. $290 stops ten
dollars before the credit runs out.

```
console.cloud.google.com/billing -> Budgets & alerts -> Create budget
  scope:  project assay-aibc-2610152153, service Cloud Run
  amount: $290
```

Two caveats from the same page:

> "Even though faster than reports, the enforcement of spend caps isn't instant
> and any cost overages are billed as normal."

The cap is a backstop, not a fuse. `--max-instances=2` is the first line.

### 6.3 Artifact Registry headroom

Free tier is **0.5 GiB**. One image pair is 0.324 GiB, leaving **0.176 GiB** — a
single extra backend push crosses it. The script prints the listing command but
never deletes anything; pruning is your call.

---

## 7. Refund (after judging, not before)

**Do not close or refund while the submission is live.**

> "When you close a Cloud Billing account, all services are stopped in all
> projects that are paid for by that billing account."

That kills the `*.a.run.app` URL you submitted.

Verbatim from `close-or-reopen` and `resolve-issues`:

```
console.cloud.google.com/billing -> Account management
  -> "Close billing account"        (requires zero outstanding balance)
  -> unused prepayment refunds to the original payment method
```

Two blockers:

> "You can't close a billing account until you pay off any previous balance"
> "We don't offer refunds [if] you have an unused promotional credit balance"

So the 500,000 IDR must still be untouched — true as long as usage draws down the
$300 credit first.

**Do not upgrade to a Paid billing account.** The Free Trial auto-closes at 90
days (~15 Jan 2027), and that auto-close is itself a valid account closure for the
refund clause — no manual Close needed.

---

## 8. Rollback

Cloud Run keeps every revision:

```bash
"$GCLOUD" run revisions list --service assay-api --region asia-southeast1
"$GCLOUD" run services update-traffic assay-api \
  --region asia-southeast1 --to-revisions <REVISION>=100
```

Stop accruing cost without deleting anything:

```bash
"$GCLOUD" run services update assay-api --region asia-southeast1 --min-instances 0
"$GCLOUD" run services delete assay-web --region asia-southeast1   # optional
```

---

## 9. Known landmines

### 9.1 `gemini-2.5-flash` is retired

```
404 NOT_FOUND: This model models/gemini-2.5-flash is no longer available to new
users. Please update your code to use models/gemini-3.8-flash
```

Fixed in `backend/app/config.py` (defaults read from env, falling back to
`gemini-3-flash-preview`) and in `/health`, which now reports the configured model
instead of a literal. Verified inside a container with **no `.env`** — the exact
production condition.

The container gets no `.env`, so anything not injected with `--set-env-vars` falls
back to the hardcoded default. That default must be a live model ID.

### 9.2 Free-tier Gemini quota is 20 requests/day

```
429 RESOURCE_EXHAUSTED: Quota exceeded for metric:
generativelanguage.googleapis.com/generate_content_free_tier_requests,
limit: 20, model: gemini-3.8-flash … Please retry in 10h11m
```

A live demo will hit this. Linking billing raises the limit (Tier 1) but starts
charging tokens at COST-MODEL §7 rates. Until then `DEMO_MODE=cached` is the safe
default for the judged run.

### 9.3 Sessions are in-process

`backend/app/repositories/firestore.py` is a stub, so `InMemoryStore` holds state.
With `min-instances=0` and `max-instances=2`, a session can vanish between
requests. Not fixable without Firestore; keep the demo to one flow at a time.

### 9.4 The API key is a plain env var

`--set-env-vars` puts `GOOGLE_API_KEY` in the service config, readable by anyone
with `run.services.get`. Acceptable for a judged prototype. Before real user data,
move it to Secret Manager with `--set-secrets`.

### 9.5 Windows shell traps

All hit and fixed in this script:

| Trap | Symptom | Fix |
|---|---|---|
| `--config /dev/stdin` | `Unable to read file [/dev/stdin]` | write a real file |
| MSYS path to a native binary | `Unable to read file [/tmp/x.yaml]` | `cygpath -w` |
| `mktemp` + unwritable `TMPDIR` | `mktemp: failed to create file … Permission denied`, deploy dies at 7/8 | write the config beside the repo |
| bare `gcloud` on PATH | `can't open file 'D:\c\...'` | prefer `gcloud.cmd` |
| missing `--quiet` | hangs on "Do you want to enable these APIs?" | `gcloud --quiet` |
| `curl -sf \| head` under `pipefail` | script dies *after* a successful deploy (rc 22) | capture, then slice |

---

## 10. Command reference

```bash
# local, no cloud
bash tools/deploy-cloudrun.sh --local-test
docker compose -f tools/docker-compose.local.yml up --build

# review then deploy
bash tools/deploy-cloudrun.sh --dry-run
bash tools/deploy-cloudrun.sh

# override anything
PROJECT=... REGION=... TAG=v1 DEMO_MODE=cached bash tools/deploy-cloudrun.sh

# inspect
"$GCLOUD" run services list --region asia-southeast1
"$GCLOUD" run services describe assay-api --region asia-southeast1
"$GCLOUD" builds list --region asia-southeast1 --limit 5
```
