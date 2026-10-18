# Team Work Breakdown Structure (WBS) & Sprint Delegation — v2.0.0
## Assay: The Active Socratic Learning Engine — 4-Day Rapid Prototype Sprint (14 – 18 October 2026)

**Submission Deadline:** 18 October 2026, 23:59 UTC+8 — **HARD DEADLINE** (submit target: 20:00 UTC+8)
**Squad Size:** 3 Developers (full parallel execution)
**Core Motto:** "Contract-First, Zero Blocker, Demo Reliability Above All"
**This document supersedes** WBS v1 (CogniForge, 4-dev, TDL + Monaco + DAG Skill Tree). Every v1 task that mentions `modules/ingest`, `interrogate/turn`, the Dual-Metric Score Card, or TDL is **void** — see §0.

---

## 0. Source of Truth & How to Read This Document

Order of authority when documents conflict:

1. [PRD.md](./PRD.md) v2.0.0 §3 (Core User Flow — CANONICAL) and §5 (team allocation) / §6 (timeline) / §8 (non-goals).
2. [API-CONTRACTS.md](./API-CONTRACTS.md) v2.0.0 — LOCKED CONTRACT (frozen 14 Oct). Single source for endpoints + schemas + state machine.
3. This document — work split, day order, per-day gates.

| Document | Purpose | Link |
|---|---|---|
| PRD v2.0.0 | Canonical flow, rubric, non-goals | [./PRD.md](./PRD.md) |
| API-CONTRACTS v2.0.0 | Endpoints, JSON, state machine | [./API-CONTRACTS.md](./API-CONTRACTS.md) |
| Demo script | 3-minute video storyboard | [./DEMO-SCRIPT.md](./DEMO-SCRIPT.md) |
| Pitch deck outline | 10 slides in English | [./PITCH-DECK-OUTLINE.md](./PITCH-DECK-OUTLINE.md) |
| Audit + judge Q&A | Judge answers, SWOT, threats | [./AUDIT.md](./AUDIT.md) |
| ADR 001 | Model routing Flash vs Pro | [./docs/adrs/001-model-selection.md](./docs/adrs/001-model-selection.md) |
| ADR 002 | Deterministic honeypot guardrails | [./docs/adrs/002-deterministic-honeypot-guardrails.md](./docs/adrs/002-deterministic-honeypot-guardrails.md) |
| ADR 003–005 | MediaPipe client-side, role taxonomy seed, honeypot catalog + variations — **files do not exist yet**, DEV 3 writes them per PRD §11 | `docs/adrs/` (TODO) |
| Empirical numbers | Honeypot, trap, verifier, JSON | [../reza-research/parts10/HASIL-TES-EMPIRIS.md](../reza-research/parts10/HASIL-TES-EMPIRIS.md) |
| Official committee deadline | Proof of 18 Oct | [../01-event-guidelines/02-timeline-schedule.md](../01-event-guidelines/02-timeline-schedule.md) |

> If a dev finds a contradiction between documents, **stop and raise it at sync** — don't pick a side alone.

---

## 1. Reality Check: Capacity vs Load (MANDATORY READING BEFORE START)

```
+--------------------------------------------------------------------------------+
|  CAPACITY                          vs   LOAD                                   |
+--------------------------------------------------------------------------------+
|  3 dev x 4 days              = 12.0 dev-day  New flow (PRD §5)   = 11.25 d-day |
|  integration overhead ~20%   = -2.4 dev-day  Required research   = 3.50 d-day  |
|  --------------------------------------------  ------------------------------  |
|  EFFECTIVE                   = 9.6 dev-day   TOTAL REQUIREMENT   = 14.75 d-day |
|                                                                                |
|                     DEFICIT = 5.15 dev-day  -->  CUTTING IS MANDATORY          |
+--------------------------------------------------------------------------------+
```

The numbers above come from [PRD.md](./PRD.md) §5 and §8, not from fresh estimates. Cut ledger:

| Block | Before cut | Action | After cut |
|---|---:|---|---:|
| Monaco + Piston + TDL (coding arena) | 1.50 | **CUT** → roadmap slide | 0.00 |
| DAG Skill Tree visual (ReactFlow) | 1.00 | **CUT** → linear chapter stepper | 0.00 |
| Dual-metric (Concept + Reasoning) | 0.50 | **CUT** → single score + calibration gap | 0.00 |
| Voice / Gemini Live | 0.50 | CUT → roadmap | 0.00 |
| Complex auth / multi-user | 0.25 | CUT → single-session demo | 0.00 |
| Multi-source input (video/audio) | 0.25 | CUT → PDF + raw text | 0.00 |
| **Subtotal cut** | **4.00** | | **10.75** |
| Report view (chart → table) | 0.25 | Trim | |
| Appeal path (full verifier → status stub) | 0.25 | Trim | |
| Accessible Mode (full → 1 toggle) | 0.25 | Trim | |
| External grounding (2 chapters → 1 chapter, cached) | 0.25 | Trim | |
| Focus Mode (6 events → 3 events) | 0.15 | Trim | |
| **Subtotal trim** | **1.15** | | **9.60 = effective capacity** |

**Never cut** (PRD §8, this is what earns the 40% Technical Merit): eval harness + numbers, verifier loop, calibration, cached fallback, honeypot, unlock gate ≥ 75.

If a new feature idea appears after Day 0: **put it on the roadmap slide, not in the repo.**

---

## 2. Role Allocation — 3 Developers

```
┌─────────────────────────────────┬─────────────────────────────────┬─────────────────────────────────┐
│ DEV 1: FRONTEND & UX            │ DEV 2: BACKEND & DATA           │ DEV 3: AI ENGINE & EVAL         │
├─────────────────────────────────┼─────────────────────────────────┼─────────────────────────────────┤
│ Folder: frontend/               │ Folder: backend/                │ Folder: eval/ + prompts/        │
│                                 │                                 │                                 │
│ • Intake screen: intent +       │ • API server (FastAPI/Express)  │ • Gemini pipeline: intent       │
│   role selector + optional PDF  │ • PDF ingest + syllabus store   │   classification, checklist gen │
│ • Realtime checklist UI         │ • Session/chapter state machine │ • Syllabus chunking + PDF-RAG   │
│ • Chapter stepper + gated reader│   LOCKED→ACTIVE_READING→        │ • Google Search grounding       │
│ • Select-word ask popover +     │   INTERVIEW→SCORED→UNLOCKED/    │   (optional, 1 chapter, cached) │
│   suggested questions           │   NEEDS_REVIEW                  │ • Socratic interviewer prompt   │
│ • Interview quiz UI             │ • Focus-event ingest            │ • Honeypot generator +          │
│ • Focus Mode camera + auto-blur │ • DEMO_MODE=cached fallback     │   4-class classifier            │
│ • Calibration slider + report   │ • Cloud Run deploy + Firestore  │ • Calibration + verifier loop   │
│                                 │                                 │ • eval/ harness + benchmarks    │
├─────────────────────────────────┼─────────────────────────────────┼─────────────────────────────────┤
│ Budget: 3.25 dev-day            │ Budget: 3.10 dev-day            │ Budget: 3.25 dev-day            │
└─────────────────────────────────┴─────────────────────────────────┴─────────────────────────────────┘
```

Folder boundary rule: a dev may read other folders, **only the owner writes**. If you need a change in someone else's folder → ask at sync, don't commit it yourself.

---

## 3. Feature Ownership Matrix (feature → owner → endpoint → artifact)

| # | Feature (PRD §4) | Owner | Endpoint (API-CONTRACTS §2) | Evidence artifact |
|---|---|---|---|---|
| F1 | Intake: intent + role selector + optional PDF | DEV 1 | `POST /intake`, `GET /roles` | Intake screenshot, JSON 201 |
| F2 | Realtime checklist (streaming + edit) | DEV 1 (UI) / DEV 3 (prompt) | `POST/PUT /intake/:id/checklist` | `checklist.partial` → `checklist.done` events |
| F3 | Syllabus synthesis + chapter metadata | DEV 2 (store) / DEV 3 (AI) | `POST /intake/:id/syllabus` | Chapter JSON + `source_pages` |
| F4 | PDF-RAG page anchor | DEV 3 | — (internal) | Honeypot claims verifiable against the page |
| F5 | External grounding (1 chapter, cached) | DEV 3 | `enable_search_grounding: true` | `cached: true` in `references[]` |
| F6 | Chapter stepper + gated reader | DEV 1 | `GET /chapters/:id` | `next_locked: true` on screen |
| F7 | Select-word Socratic ask | DEV 1 (popover) / DEV 3 (prompt) | `POST /chapters/:id/ask` | `gave_direct_answer: false` |
| F8 | Suggested questions (multi-word) | DEV 1 / DEV 3 | `GET /chapters/:id/suggestions` | 3 questions per selection |
| F9 | Multi-turn interview quiz (2-3 rounds) | DEV 1 (UI) / DEV 3 (prompt) | `POST /chapters/:id/interview/{start,turn,finalize}` | `running_score`, `is_concluded` |
| F10 | Honeypot generator + 4-class classifier | DEV 3 | (inside `interview/turn`) | `honeypot_verdict.result` + score ± |
| F11 | Focus Mode (MediaPipe on-device) + auto-blur | DEV 1 (ML/UI) / DEV 2 (ingest) | `POST /chapters/:id/focus-events` | `video_transmitted: false`, `assisted` flag |
| F12 | Accessible Mode (camera off) | DEV 1 / DEV 2 | same as F11 | `integrity_flag: assisted_unverified` |
| F13 | Single score per chapter + threshold 75 | DEV 3 (compute) / DEV 2 (state) | `interview/finalize` | `chapter_score` + state transition |
| F14 | Calibration gap (predict before reveal) | DEV 1 (slider) / DEV 3 (label) | `POST /chapters/:id/calibration` | `calibration_gap` + `label` |
| F15 | Verifier loop + appeal path (stub) | DEV 3 | `interview/finalize`, `POST /chapters/:id/appeal` | `verifier.status` |
| F16 | Final report | DEV 1 (view) / DEV 2 (aggregation) | `GET /report/:sessionId` | Report JSON + screenshot |
| F17 | Cached fallback (2 scenarios) | DEV 2 | `DEMO_MODE=cached` / header | `LOCAL_DETERMINISTIC_CACHE` banner |
| F18 | Eval harness + numbers | DEV 3 | — (offline) | `eval/results/*.jsonl` + table |

**CUT (do not build, goes on the roadmap slide):** Monaco + Piston + TDL, DAG Skill Tree (ReactFlow), dual-metric, voice/Gemini Live, multi-user auth, video/audio input. Reference: [PRD.md](./PRD.md) §8.

---

## 4. Day-by-Day Task Detail (Day-by-Day Sprint)

### Day 0 — Wednesday, 14 October (tonight: setup & baseline)

**DEV 1 — Frontend**
- Init the Next.js 15 project (App Router, TypeScript, Tailwind) in `frontend/`: `npx create-next-app@latest frontend --typescript --tailwind --app`.
- Create the route skeleton: `/intake`, `/checklist`, `/syllabus`, `/chapter/[id]`, `/interview/[id]`, `/report/[sessionId]`.
- Copy **every JSON example from [API-CONTRACTS.md](./API-CONTRACTS.md) §2** into `frontend/mocks/*.json` — these are what we use until the backend is ready (No Blocker Rule §6.1).
- Static render: intake screen (3 inputs, no "Summarize" button anywhere) + checklist with checkboxes.

**DEV 2 — Backend**
- Init the API server (FastAPI or Express) in `backend/`, prefix `/api/v1`.
- Implement `POST /api/v1/intake` + `GET /api/v1/roles` (9 role seeds + `Others`, see [API-CONTRACTS.md](./API-CONTRACTS.md) §2.1).
- Session store in memory first (Firestore tomorrow), plus fallback middleware: header `x-demo-mode: cached` → return the local cache.
- Write the backend `Dockerfile` (do not deploy tonight, deploy Day 1/3).

**DEV 3 — AI Engine**
- Set up the Gemini connection via the **Google Gen AI SDK** (`google-genai` / `@google/genai`), env `GOOGLE_API_KEY` / Vertex project.
- Test `response_schema` (JSON Schema in [API-CONTRACTS.md](./API-CONTRACTS.md) §4) — target: parse with no exceptions.
- Draft the Socratic interviewer prompt + deterministic honeypot catalog (ADR 002), **10 terms** for tonight's test.
- Create `eval/` (see §6.5): model-calling harness + 4-class classifier. Follow the methodology in [HASIL-TES-EMPIRIS.md](../reza-research/parts10/HASIL-TES-EMPIRIS.md) so the new numbers can be compared against the baseline (n=80).

**Day 0 Gate:** API-CONTRACTS v2 frozen; 3 repo folders (`frontend/`, `backend/`, `eval/`) running locally; mock JSON complete; 10 honeypot terms revalidated.

---

### Day 1 — Thursday, 15 October (intake → checklist → syllabus)

**DEV 1 — Frontend**
- Final intake screen: free-text intent (min 3 words, validated), role selector from `GET /roles`, the `Others` option appears automatically when `suggested_others: true`, optional PDF slot with a clear "no document" state.
- Realtime checklist UI: consume SSE `checklist.partial` per item → `checklist.done`; show the checkbox, `confidence`, and `origin` tag (`document` / `role_taxonomy` / `grounded_external`).
- Uncheck/check + `PUT /intake/:id/checklist` → continue to `/syllabus`.

**DEV 2 — Backend**
- `POST /intake/:sessionId/checklist` (JSON variant + `stream: true`), `PUT /intake/:sessionId/checklist`.
- PDF ingest: text extraction + page numbers (page-anchored), persist to the store.
- `POST /intake/:sessionId/syllabus` — handler + persist syllabus/chapter to Firestore, respond with the schema in [API-CONTRACTS.md](./API-CONTRACTS.md) §2.3.
- First deploy to Cloud Run (make sure the `*.a.run.app` URL is live), Cloud Logging enabled.

**DEV 3 — AI Engine**
- Intent classification + detection of a role that doesn't match a seed → `suggested_others: true` (ADR 004).
- Checklist generation prompt: emit items + `origin` + `confidence`.
- Syllabus chunking: structured chapters (`title`, `order`, `objectives`, `estimated_reading_minutes`, `source_pages`) — not blind 300-600-word chunks.
- PDF-RAG: page anchor per chapter; the **no-PDF** path → `source_mode: role_taxonomy_generated`.
- External grounding: enable for **1 chapter only**, cache results to Firestore (fall back to cache on API error).

**Day 1 Gate:** from a single intake screen, the checklist streams in and can be edited; submit → ≥ 3 chapters with `source_pages`; the no-PDF path still produces chapters tagged with `source_mode`.

---

### Day 2 — Friday, 16 October (chapter reader + interview + honeypot)

**DEV 1 — Frontend**
- **Linear chapter stepper** (not a DAG): number, title, status badge from the state machine.
- Gated reader: chapter content, references panel (`document` page anchor + `grounded_external` with `cached: true`), `Next` button disabled while `next_locked: true`.
- Select-word popover: call `POST /chapters/:id/ask`, show the Socratic reply + `hint_level` + `citations`, and **surface `gave_direct_answer: false`** in the response panel (this is the proof of the thesis, don't hide it).
- Multi-word selection → `GET /chapters/:id/suggestions` → 3 clickable questions.
- Interview UI: multi-turn, response-pressure timer (starts after the question finishes streaming), honeypot verdict banner.

**DEV 2 — Backend**
- `GET /chapters/:chapterId` + the full state machine: `LOCKED → ACTIVE_READING → INTERVIEW → SCORED → UNLOCKED/NEEDS_REVIEW` ([API-CONTRACTS.md](./API-CONTRACTS.md) §1). Honeypot does **not** change state, it only fills `honeypot_score`.
- `POST /chapters/:id/interview/{start,turn,finalize}`; persist turn history; forward `client_telemetry` (`paste_detected`, `duration_seconds`, `keystroke_cpm`).
- Unlock threshold ≥ 75, `< 75` → `NEEDS_REVIEW` (retry), not a dead end.
- `/report/:sessionId` endpoint (basic aggregation) so DEV 1 can wire it earlier.

**DEV 3 — AI Engine**
- Socratic interviewer prompt: 2-3 rounds, inferential/HOTS questions + adaptive follow-up (not "what is the definition of X").
- Honeypot generator: deterministic catalog + term variations (ADR 002 + ADR 005) so it can't be memorized.
- 4-class classifier → score: `CRITICAL_REJECTION` +2, `AI_HALLUCINATION_COPYPASTE` −2, `UNVERIFIED_HONEST` 0, `EVASIVE` −1.
- Verifier loop: second model (Gemini Pro) reviews the score; `verifier.status` = `agreed` / `uncertain`.

**Day 2 Gate:** chapter 2 stays `LOCKED` until chapter 1's score ≥ 75; pasting an outside LLM answer → `AI_HALLUCINATION_COPYPASTE` (−2); rejecting the premise → `CRITICAL_REJECTION` (+2). Both must be visible in the UI, not just in JSON.

---

### Day 3 — Saturday, 17 October (Focus Mode + scoring + calibration + fallback)

**DEV 1 — Frontend**
- Focus Mode: camera on, MediaPipe on-device (head-pose/gaze drift, face count > 1, tab blur). Detected → **auto-blur the page** + `assisted` badge.
- Accessible Mode: single toggle (camera off, blur off, relaxed timer) → `assisted_unverified` status.
- Calibration slider: user predicts the score (0-100) **before** reveal → show `predicted_score`, `actual_score`, `calibration_gap`, `label` (`overconfident` / `underconfident` / `well_calibrated`).
- Report view: score per chapter, mean calibration gap, integrity flags, honeypot verdict log, appeal button (stub).

**DEV 2 — Backend**
- `POST /chapters/:id/focus-events`: accept **boolean events only**, `video_transmitted` must be `false` (ADR 003), respond with `integrity_flag` + `auto_blur` + `summary`.
- `DEMO_MODE=cached` (+ header `x-demo-mode: cached`): 2 pre-cached scenarios — success flow (`CRITICAL_REJECTION`, high score, unlock) and caught flow (`AI_HALLUCINATION_COPYPASTE`, score drops, integrity flag). The cache also stores grounding results.
- Automatic fallback when Gemini errors `429/500/503`, return `{ fallback_active: true, source: "LOCAL_DETERMINISTIC_CACHE" }` with no exception.
- Final Cloud Run deploy + verify the public URL from an external network (phone, not just localhost).

**DEV 3 — AI Engine**
- Deterministic scoring from the LLM classification (ADR 002): single `chapter_score` 0-100 + `reasoning_score` + `integrity_score` + `honeypot_score`. **Not** two parallel metrics.
- Calibration label + appeal handler (verifier as reviewer, outcome `upheld` / `revised` / `uncertain`).
- **Final eval harness** in `eval/`: run the suite → save `eval/results/*.jsonl` + a summary table (honeypot hallucination rate, trap effectiveness per type, sycophancy gap, verifier catch rate, valid-JSON rate).
- Every number for the deck/README is taken **only** from `eval/results/` or [HASIL-TES-EMPIRIS.md](../reza-research/parts10/HASIL-TES-EMPIRIS.md).

**Day 3 Gate:** the full intake → report flow runs twice back to back: once online, once `DEMO_MODE=cached`. Zero empty spinners. Eval numbers saved to file.

---

### Day 4 — Sunday, 18 October (deploy + video + deck + submit)

| Time (UTC+7) | Activity | Owner | Output |
|---|---|---|---|
| 09:00 – 11:00 | Final deploy + smoke test of 2 cached scenarios from a phone | DEV 2 | Cloud Run URL live, clean logs |
| 11:00 – 13:00 | Dry run + record the 3-minute video (1080p, EN, cached) | DEV 1 | Video file ready to upload |
| 13:00 – 16:00 | 10-slide EN deck PDF (from [PITCH-DECK-OUTLINE.md](./PITCH-DECK-OUTLINE.md)) + repo README + architecture diagram | DEV 1 + DEV 3 | `deck.pdf`, `README.md` |
| 16:00 – 18:00 | Git audit (no `.env`/tokens), upload to YouTube, tidy URLs | DEV 2 | Clean public repo |
| 18:00 – 19:30 | Submit to the Hack2skill portal: video + deck PDF + Cloud Run URL + GitHub URL | All | Submission confirmation |
| **before 20:00** | **SUBMIT DONE** — 4-hour buffer before 23:59 UTC+8 | — | — |
| 20:00 – 23:59 | Buffer. **Code freeze.** If there's a bug, fix it in the video/deck, not in the repo | — | — |

**Day 4 Gate:** submission sent before 20:00 UTC+8; public repo with no secrets; 180-second video; 10-slide English deck (PRD §7: UI, README, deck, video = English).

---

## 5. Checkpoints & Definition of Done

**Mandatory sync (No Blocker Rule §6.3): 12:00 and 21:00, 15 minutes, fixed agenda:**

1. Blockers I have → who unblocks them.
2. Contract changes I need (if any).
3. What works **right now** (30-second demo, not a description).

**EOD freeze, every day at 23:00 (UTC+7):**

| Day | Must be green at EOD | If red |
|---|---|---|
| 0 | 3 folders running, mock JSON complete, 10 honeypot terms validated | Use mocks, move on to Day 1 |
| 1 | intake → checklist → syllabus (with & without PDF) | Frontend continues from mocks; DEV 3 cuts grounding |
| 2 | locked/unlock gate + both honeypot verdicts visible in the UI | Interview becomes 2 fixed rounds, adaptive follow-up dropped |
| 3 | full flow online **and** cached, eval numbers saved | Execute the §7 backup cuts, no overtime on new features |
| 4 | submission sent | Priority: video + deck + live URL. The last feature gets sacrificed |

**Rollback rule:** a feature that doesn't work at EOD is rolled back to mock/cached. No half-working feature carries into the next day — that's what kills the demo in front of the judges.

---

## 6. Mutually Locking Commitments (No Blocker Rule)

### 6.1 Frontend does not wait for backend — use mocks
The frontend **must** be able to run fully from `frontend/mocks/*.json` copied from the JSON examples in [API-CONTRACTS.md](./API-CONTRACTS.md). If an endpoint doesn't exist yet, the frontend switches its base URL to the mock adapter — it does not stop. The backend chases the schema, not the other way around.

### 6.2 Google AI SDK only
All product code uses **only the Google AI SDK** (Gemini via Vertex AI / Google Gen AI SDK). Installing `openai`, `anthropic`, or `cohere` in the product's `package.json` / `requirements.txt` is forbidden — breaking the event rules = zero risk on the 40% Technical Merit (PRD §7).

Narrow exception: harnesses in `eval/` may call non-Google models **through an HTTP gateway** to measure trap effectiveness (research methodology in [HASIL-TES-EMPIRIS.md](../reza-research/parts10/HASIL-TES-EMPIRIS.md)). Conditions: it must not become a product runtime dependency, must not be imported by `backend/`, and must not be presented as part of Assay's architecture in the deck.

### 6.3 Daily sync
15-minute sync at **12:00 and 21:00** (UTC+7). A blocker hanging for > 2 hours must be raised in the channel, not buried. A blocker without a solution = drop to the cached fallback and keep working.

### 6.4 Frozen contract
After Day 0, changes to [API-CONTRACTS.md](./API-CONTRACTS.md) only happen by agreement of all three and must be reflected in `frontend/mocks/` immediately. An endpoint/field that changes without a mock update = a blocker for everyone.

### 6.5 Numbers only from auditable sources
Every number in the deck, README, and video must be traceable to `eval/results/` or [HASIL-TES-EMPIRIS.md](../reza-research/parts10/HASIL-TES-EMPIRIS.md). Inventing numbers is forbidden (PRD §9 — the v1 deck once wrote "91.3% / 640ms" with no source; don't repeat it).

### 6.6 Folder boundaries
`frontend/` belongs to DEV 1, `backend/` to DEV 2, `eval/` + `prompts/` to DEV 3. Cross-folder work needs the owner's permission at sync.

---

## 7. Backup Cut Order (if Day 3 is still red)

Execute from the top, one at a time, until the load fits capacity. Don't improvise the order.

| # | Cut | Impact on the demo |
|---|---|---|
| 1 | Appeal path → stub (show `under_review`, no second model) | Small — appeal isn't a demo moment |
| 2 | Google Search grounding → off entirely, PDF-RAG only | Small — grounding is just a supplement |
| 3 | Multi-turn interview → 2 fixed rounds, adaptive follow-up dropped | Medium — judge Q&A answers are already prepared in [AUDIT.md](./AUDIT.md) §10 |
| 4 | Focus Mode → 1 event (`MULTIPLE_FACES`) + tab blur | Medium — sell it as an "integrity signal", don't claim anti-cheat |
| 5 | Report trend chart → number table | Small |
| — | **Never cut:** honeypot, unlock gate ≥ 75, calibration gap, cached fallback, eval harness + numbers | — |

---

## 8. Sprint Risks & Action Triggers

| # | Risk | Observable trigger | Action |
|---|---|---|---|
| R1 | Scope too big (14.75 vs 9.6 dev-day) | Day 2 EOD red | Run §7, don't work overtime |
| R2 | Honeypot fails (outside LLM rejects the hallucination) | Re-test rate < 40% | Use backup terms of the `fictional_term` type already proven in [HASIL-TES-EMPIRIS.md](../reza-research/parts10/HASIL-TES-EMPIRIS.md) P2 |
| R3 | LLM grading feels subjective | Judges ask about score consistency | Show ADR 002 + `verifier.status` + appeal path |
| R4 | Gemini down / rate limited during demo | 429/500/503 errors | `DEMO_MODE=cached` 2 scenarios; never record without cached |
| R5 | "Anti-cheat" dismantled by judges | "Can it be bypassed?" question | Don't claim anti-cheat. Sell "Focus Mode / integrity signal" + Accessible Mode (Q&A in [AUDIT.md](./AUDIT.md) §10) |
| R6 | MediaPipe fails to load on the recording device | Camera/model won't init on Day 3 morning | Fallback: tab-blur + `CAMERA_OFF` event, still show the Focus Mode panel |
| R7 | Cached honeypot data goes stale | Cached scenario doesn't match the latest UI | Regenerate the cache every time the schema changes (DEV 2, Day 3) |

---

## 9. Submission Artifacts (Day 4 Checklist)

- [ ] Cloud Run URL live (`*.a.run.app`), tested from an external network
- [ ] Public GitHub URL, no `.env` / tokens / keys
- [ ] 3-minute demo video, 1080p, English voiceover, no background music
- [ ] 10-slide English deck PDF
- [ ] Repo README: how to run, architecture, how to enable `DEMO_MODE=cached`
- [ ] Eval numbers table from `eval/results/`
- [ ] Submission sent on the Hack2skill portal **before 20:00 UTC+8 (18 Oct 2026)**

---

## 10. Numbers You May Use (and one that must be verified)

Source: [HASIL-TES-EMPIRIS.md](../reza-research/parts10/HASIL-TES-EMPIRIS.md) — don't round up, don't add.

| Claim | Number | Sample | Status |
|---|---|---|---|
| Honeypot hallucination rate (all models) | 54% | n = 80 calls, 4 models | Safe |
| — gemini-flash-medium / deepseek-v4-pro / deepseek-v4-flash / deepseek-v4.1-flash | 75% / 70% / 45% / 25% | 20 calls each | Safe |
| Trap effectiveness: `trap_number` | 58% | n = 48 | Safe |
| Trap effectiveness: `false_premise` / `over_claim` | 25% / 25% | n = 48 | Safe |
| Verifier loop catches hallucination | 13/20 (65%) | 20 hallucinated answers | Safe |
| Structured output valid JSON | 4/4 (100%) | 4 schema calls | Safe |
| Trap effectiveness: `fictional_term` | **100%** (10 comply / 0 pushback / 2 error) — **RESOLVED**: the 67% in the old PRD §9 was wrong (ERRORs were counted as PUSHBACK) | n = 12 valid | Safe. Use 100% and state n=12 |
| Latency | 26s average across models | — | **Do not use in the video** (not demo-relevant) |
| Any number not in this table | — | — | Forbidden in the submission |

---

**Closing:** capacity is 9.6 dev-day, the load is 14.75. This plan has already cut 5.15 dev-day to close that gap. If anyone adds a feature outside the §3 table, that isn't extra work — it's debt paid on Day 4 with a video that fails to record.