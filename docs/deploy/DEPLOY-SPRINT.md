# Deploy Sprint — 15 minutes, from "billing just opened" to live URL

Paste this in one sitting. Times are measured on this machine, not guessed.

Prereqs already done: images build, engine ships, proxy works, 217 backend tests +
25 engine tests pass. See `docs/deploy/DEPLOY-RUNBOOK.md` for the why behind each step.

---

## Minute 0–2 — confirm billing is actually open

```bash
export GCLOUD="/c/Users/Reza/AppData/Local/Google/Cloud SDK/google-cloud-sdk/bin/gcloud.cmd"

"$GCLOUD" billing projects describe assay-aibc-2610152153 --format='value(billingEnabled)'
```

**Must print `True`.** If it prints `False`, stop — nothing below will work.

If you just paid the prepayment, give it 2–3 minutes. Then re-run the command.

---

## Minute 2–3 — review the plan

```bash
cd D:/Project/assay
bash tools/deploy-cloudrun.sh --dry-run
```

Exit 0. Read the two `run deploy` lines. Confirm:

```
--region asia-southeast1   --min-instances 0   --max-instances 2
--cpu 1 --memory 512Mi     GOOGLE_API_KEY=***REDACTED***
```

No local build runs here — Cloud Build does the building. If you want the local
build-and-verify pass too, add `--verify-local` (about 4 extra minutes, and it
proves nothing that step 7/8 does not already prove on a first deploy).

---

## Minute 3–11 — deploy

```bash
bash tools/deploy-cloudrun.sh
```

Expect roughly this, in order:

| Step | Typical duration | What it does |
|---|---|---|
| 1/8 Billing gate | ~3 s | confirms `billingEnabled=True`, else aborts |
| 2/8 Build locally | 0 s | **skipped** on a full deploy |
| 3/8 Engine check | 0 s | skipped (no local image) |
| 4/8 API smoke | 0 s | skipped (no local image) |
| 5/8 Enable APIs | 1–3 min | first time only; ~5 s after that |
| 6/8 Artifact Registry | ~5 s | creates the repo once |
| 7/8 Cloud Build | 5–8 min | builds + pushes both images |
| 8/8 Cloud Run deploy | 1–2 min | two services, api then web |

The long pole is 7/8. That is a first build with no layer cache; later builds are
much faster.

If it fails, the step number tells you where:

- **1/8** → billing not open
- **5/8** → missing `serviceusage.services.enable` (you have it, verified)
- **7/8** → Dockerfile fails in the cloud, or source upload too large
- **8/8** → quota, org policy, or missing `run.services.create` (you have it)

---

## Minute 11–13 — verify from outside

The script prints the two URLs at the end. Then:

```bash
API_URL=<the api url it printed>
WEB_URL=<the web url it printed>

curl -s $API_URL/health
# {"status":"healthy",...,"engine":"Google gemini-3-flash-preview","demo_mode":"live",...}

curl -s $API_URL/health/cache     # ok:true
curl -s $WEB_URL/healthz          # ok
curl -s $WEB_URL/api/v1/roles     # 9-role taxonomy through the nginx proxy
```

Prove it is really on GCP (this is what a judge sees):

```bash
curl -sI $WEB_URL | grep -iE 'server|via|x-cloud'
```

Expect `server: Google Frontend` and/or `via: 1.1 google`. A Vercel or Railway
deployment would say so instead.

---

## Minute 13–15 — the only test that counts

Open `$WEB_URL` **on your phone, on mobile data.** Walk the demo once:

```
intake -> checklist -> syllabus -> interview turn -> report
```

Then set the spend cap while you remember:

```
console.cloud.google.com/billing -> Budgets & alerts -> Create budget
  scope:  project assay-aibc-2610152153, service Cloud Run
  amount: $290
```

$290, not $5 — spend caps use gross cost and ignore the $300 credit.

---

## If the demo is judged and the quota bites

Free-tier Gemini is **20 requests/day**. If a judge hits that, the app falls back
per request, but the cleanest answer is to pin the judged run to fixtures:

```bash
# rebuild + redeploy the web bundle with DEMO_MODE=cached
DEMO_MODE=cached bash tools/deploy-cloudrun.sh
```

That makes every API call deterministic and instant (measured: 23 ms vs 6,223 ms).

---

## Rollback if something is wrong

```bash
"$GCLOUD" run revisions list --service assay-api --region asia-southeast1
"$GCLOUD" run services update-traffic assay-api \
  --region asia-southeast1 --to-revisions <REVISION>=100
```

---

## What is already proven vs still unproven

**Proven on this machine:**

- both images build; `import ai` succeeds inside the API image
- `/health` reports the configured model with **no `.env`** present
- nginx proxies `/api` to the API container; SPA deep links return `index.html`
- `cached` mode answers the checklist in 23 ms
- deploy script: dry-run clean, key redacted, fails fast and builds nothing when
  billing is closed, all Windows shell traps fixed
- 217 backend tests + 25 engine tests pass; frontend `tsc && vite build` passes
- Cloud Build upload is 1.1 MB / 138 files (was 439 MB)

**Unproven until billing opens** — do not claim these before you see them:

- Cloud Build actually runs the Dockerfiles in GCP
- images land in Artifact Registry
- `gcloud run deploy` creates both services
- a real Cloud Run cold start (local measurement was 8.4 s warm-disk)
