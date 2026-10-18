# Assay — The Active Socratic Learning Engine

> **Every AI study tool answers questions. Assay questions your answers.**

[![Event](https://img.shields.io/badge/AI%20Builder%20Cup-2026-blue.svg)](https://hack2skill.com)
[![Track](https://img.shields.io/badge/Track%204-Media%2C%20Content%20%26%20Digital%20Experiences-blueviolet.svg)](#track-alignment)
[![Stack](https://img.shields.io/badge/React%20%2B%20Vite-FastAPI%20%2B%20Gemini-orange.svg)](#architecture)
[![Deploy](https://img.shields.io/badge/Google%20Cloud%20Run-asia--southeast1-green.svg)](docs/deploy/DEPLOY-RUNBOOK.md)
[![Tests](https://img.shields.io/badge/tests-274%20passing-brightgreen.svg)](#verification)
[![License](https://img.shields.io/badge/license-MIT-lightgrey.svg)](LICENSE)

![Assay intake screen](docs/submission/assets/intake.png)

---

## What this is

Assay is a study tool that refuses to hand you answers.

You give it a topic or a PDF, and it builds a gated syllabus — then makes you
defend each chapter in a Socratic interview before the next one unlocks. It plants
fabricated concepts in the material to catch you pasting from another LLM, and it
runs focus tracking entirely on-device so no webcam frame ever leaves your browser.

The bet: the bottleneck in AI-assisted learning is not access to explanations. It
is that reading a good explanation feels like understanding it.

## The problem

Generative AI made summaries free. That is the problem, not the win.

| Signal | Figure | Source |
|---|---|---|
| Students using AI for coursework | 95% | HEPI 2026 |
| Report AI degrading their own reasoning | 67% | RAND, Mar 2026 |
| Unguarded AI assistants → retention drop | 17% | arXiv:2606.26181 |

An assistant that answers on demand removes the retrieval practice that makes
learning stick. Assay inverts it: the AI's job is to interrogate, not to explain.

## How it works

```
intent + role + optional PDF
        │
        ▼
  scope checklist  ──►  gated syllabus  ──►  chapter interview  ──►  audit report
  (live stream)         (page-anchored)      (score ≥ 75 unlocks)    (calibration gap)
        │                                            │
        │                                            ▼
        │                                     honeypot probes
        └──────────────────────────────────  (fabricated concepts
                                              catch pasted answers)
```

Eight behaviours, each verifiable in the live demo:

1. **Intake** — intent, target role, optional PDF. Classified into a role taxonomy.
2. **Live scope checklist** — topics streamed with their `origin`
   (`document` / `role_taxonomy` / `grounded_external`), so you can see what came
   from where and curate before committing.
3. **Structured syllabus** — chunks into gated chapters anchored to page numbers.
4. **Gated progression** — later chapters stay `LOCKED` until the interview score
   clears 75.
5. **Inline Socratic inquiry** — select any phrase, get a counter-question
   (`gave_direct_answer: false`), never the answer.
6. **Honeypot injection** — plausible fictional concepts planted in the material.
   If you explain one confidently, you were pasting.
7. **On-device focus mode** — MediaPipe gaze and multi-face signals in the browser,
   auto-blur on drift. `video_transmitted: false`, always.
8. **Calibration report** — you predict your score before it is revealed; the
   report measures the gap.

## Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│  Browser                                                         │
│  React 18 · Vite · TypeScript · Tailwind                         │
│  Intake · Checklist · Reader · Interview · Report                │
│  MediaPipe focus tracking (on-device, no frames uploaded)        │
└───────────────────────────┬──────────────────────────────────────┘
                            │ REST + SSE   /api/v1
                            │ x-demo-mode: cached | live
                            ▼
┌──────────────────────────────────────────────────────────────────┐
│  assay-api — Cloud Run, asia-southeast1                          │
│  FastAPI · Python 3.11 · Uvicorn                                 │
│  27 routes · chapter state machine · PyMuPDF extractor           │
│  ai/ engine: interrogator · honeypot catalog · verifier loop     │
└───────────────────────────┬──────────────────────────────────────┘
                            │ google-genai SDK
                            ▼
                   Gemini 3 Flash  (AI Studio)
```

Two containers, not three. The AI engine (`ai/`) is a Python package imported
directly by the backend — not a separate service. `assay-web` is nginx serving the
built SPA and proxying `/api` to `assay-api`, so the browser only ever talks to one
origin: no CORS, and the API URL is injected at container start rather than baked
into the bundle.

Deployment details, costs and the runbook: [`docs/deploy/`](docs/deploy/).

## Quick start

### Docker — one command

```bash
git clone https://github.com/rafidaaziz23/assay.git
cd assay
cp backend/.env.example .env      # then set GOOGLE_API_KEY, or leave DEMO_MODE=cached
docker compose -f tools/docker-compose.local.yml up --build
```

Open <http://localhost:8080>. No API key needed if `DEMO_MODE=cached`.

### Native

```bash
# backend
cd backend && python -m venv .venv && .venv/Scripts/activate   # Linux: source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env            # set GOOGLE_API_KEY
uvicorn app.main:app --reload --port 8000

# frontend (second terminal)
cd frontend && npm ci && npm run dev     # http://localhost:5173
```

Requires Python 3.11+, Node 20+. Interactive API docs at `/docs`.

## Verification

Every number here was produced by a command in this repo, not estimated.

| Check | Command | Result |
|---|---|---|
| Backend tests | `cd backend && pytest -q` | **249 passed** |
| Engine tests | `pytest ai/tests -q` | **25 passed** |
| Frontend build | `cd frontend && npm run build` | `tsc && vite build` clean |
| Deploy script | `bash tools/deploy-cloudrun.sh --local-test` | builds, engine imports, `/health` OK |

```
backend    36 files   5,986 lines   Python
ai          9 files   1,145 lines   Python
eval       13 files   1,011 lines   Python
frontend   41 files   9,251 lines   TypeScript
```

## Evaluation

Two layers, labelled honestly — the difference matters when someone checks.

**Runs offline, right now:**

```bash
python eval/run_benchmarks.py     # 4/4 classifier cases, no model calls
```

This is a unit test of the deterministic honeypot classifier, not a model
benchmark. It proves the classifier is wired correctly and gives the same answer
every time.

**Cited external audit** — `eval/results/baseline_empirical.json`, dated
2026-10-14, n=80 calls across 4 models. The raw dataset is **not in this repo**
(it lives in a separate research document), so these figures are cited, not
reproducible here. Stated as such because a judge should be able to tell the
difference.

| Metric | Rate | Sample |
|---|---|---|
| Honeypot hallucination, all models | **54%** | n = 80 |
| · `gemini-flash-medium` | 75% | 20 |
| · `deepseek-v4-pro` | 70% | 20 |
| · `deepseek-v4-flash` | 45% | 20 |
| · `deepseek-v4.1-flash` | 25% | 20 |
| Trap `fictional_term` | **100%** comply | n = 12 |
| Trap `trap_number` | 58% | n = 48 |
| Trap `false_premise` | 25% | n = 48 |
| Verifier catch rate | **65%** (13/20) | n = 20 |
| JSON schema validity | 100% | n = 4 |

**In-repo evidence:** 28 captured model responses under
[`eval/results/`](eval/results/), real text of models explaining fabricated
concepts. What is missing is a `model` field on each record, so per-model
attribution comes from the audit above rather than from the stored data.

A 54% rate is the point: models will confidently explain things that do not
exist. That is what makes a pasted answer detectable.

On the non-Google rows: the competition requires the **product** to run on Google
AI models, which Assay does — Gemini only, verified by grep across `backend/`,
`ai/`, `frontend/` and `prompts/`. Measuring competitor models as adversarial
baselines is not part of the product path.

## Zero-crash demo mode

Live demos meet rate limits. Assay treats that as a design constraint, not an
accident:

- **`DEMO_MODE=cached`** — the backend serves deterministic fixtures, zero external
  calls. Measured latency: **23 ms** versus 6,223 ms live.
- **Per-request fallback** — on `429`/`500`/`503`, the backend degrades that one
  response instead of failing the flow.
- **Frontend mock fallback** — if the API is unreachable, the SPA serves
  `frontend/src/mocks/*.json`.

The judged run uses `cached`. Everything else uses `live`.

## Repository layout

```
├── backend/          FastAPI app · 27 routes · PyMuPDF · Dockerfile
├── frontend/         React + Vite SPA · nginx Dockerfile · proxy template
├── ai/               Socratic engine package (imported by backend)
├── prompts/          System prompts + deterministic honeypot catalog
├── eval/             Benchmark harness + audited results
├── tools/            deploy-cloudrun.sh · compose · gates · deck builder
└── docs/
    ├── product/      PRD · user flow · demo script · planner
    ├── architecture/ ARCHITECTURE · API contracts
    ├── deploy/       Runbook · sprint checklist · cost model
    ├── logs/         DEV3 overnight brief + execution log
    ├── research/     Competitive analysis · proctoring analysis
    ├── process/      Task delegation · audits · recruitment
    ├── pitch/        Pitch deck outline
    ├── assets/       Screenshots
    └── submission/   Deck (pptx) + preview slides
```

## Track alignment

**Track 4 — Media, Content & Digital Experiences.** Assay transforms how
educational content is *understood and experienced*: content becomes a gated
dialogue rather than a text to skim.

Hard requirements, and where they are satisfied:

- **Google AI models only** — `google-genai` SDK, Gemini 3 Flash. No `openai`,
  `anthropic` or `cohere` in any dependency file.
- **Deployed on Google Cloud** — Cloud Run, `asia-southeast1`. See
  [`docs/deploy/DEPLOY-RUNBOOK.md`](docs/deploy/DEPLOY-RUNBOOK.md).
- **Fresh build** — all commits fall inside the submission window.

## Known limitations

Stated plainly, because a judge will find them anyway:

- **Session state depends on credentials.** `repositories/firestore.py` implements a
  `FirestoreStore`, and `get_store()` selects it when a service account is present;
  without one it falls back to `InMemoryStore`. On Cloud Run with no Firestore
  credentials injected, state is per-container — and with `min-instances=0` plus
  `max-instances=2` a session can be lost between requests. Inject
  `FIREBASE_CREDENTIALS_PATH` (or use the attached service account) to persist.
- **Focus mode is heuristic.** MediaPipe gaze and face-count signals are advisory,
  not a proctoring guarantee.
- **Free-tier Gemini is 20 requests/day** per project. The judged run uses
  `DEMO_MODE=cached` for this reason.
- **Honeypot detection is a signal, not proof.** A confident wrong explanation
  suggests pasting; it does not prove it.

## Team

Three developers, four-day sprint.

| Role | Owns | Built |
|---|---|---|
| **DEV 1** | `frontend/` | Intake, checklist, gated reader, Socratic popover, focus mode UI, calibration, report |
| **DEV 2** | `backend/` | 22 API routes, chapter state machine, PyMuPDF extractor, cached fallback, Cloud Run deploy |
| **DEV 3** | `ai/`, `prompts/`, `eval/` | Engine, Socratic prompts, honeypot catalog, verifier loop, benchmark suite |

Detailed split: [`docs/process/TEAM-TASK-DELEGATION.md`](docs/process/TEAM-TASK-DELEGATION.md).

## License

MIT — see [LICENSE](LICENSE).

Built for the **Google Cloud AI Builder Cup 2026** (Hack2skill), Track 4.
