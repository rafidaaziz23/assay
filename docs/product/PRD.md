# Product Requirements Document (PRD) — v2.0.0
## Assay: The Active Socratic Learning Engine
*(codename repo: Active Learning Engine — `active-learning-engine/`)*

**Event:** AI Builder Cup 2026 (Google Cloud x Hack2skill, JAPAC)
**Target Submission Deadline:** 18 October 2026, 23:59 UTC+8 — **HARD DEADLINE**
**Track Alignment:** Track 4 (Media, Content & Digital Experiences — Adaptive Learning) — **single track**
**Author / Core Team:** AI Builder Cup Squad (3 developers)
**Document Version:** 2.0.0
**Status:** OPERATIONAL CONTRACT — binding. This document supersedes PRD v1.0.0.

---

## 0. Changelog v1.0.0 → v2.0.0

Summary of what changed, so nobody gets confused reading two versions.

| Area | v1.0.0 | v2.0.0 | Reason |
|---|---|---|---|
| Product name | CogniForge | **Assay** | "Cogni-" is an AI-slop pattern; "Assay" = a test of metal purity + homophone of "essay" |
| Entry point | PDF upload (required) | Intent input + Role selector + PDF (**optional**) | New flow: the user starts from a learning intent, not a document |
| Track | Track 4 **and** Track 5 | Track 4 only | Rules: 1 team = 1 track |
| Deadline | October 19 | **October 18** | Official organizer deadline |
| Team | 4 developers | **3 developers** | Squad reality |
| Curriculum | 300-600 word chunks → concept node | Intent+role → checklist → **chapter syllabus** | New flow |
| Score | Dual-metric (Concept + Reasoning) | **Single score + Calibration Gap** | Cheaper, stronger demo (research C1) |
| Honeypot | Hard gate (hit = fail) | **Score dimension** (+2/-2/0/-1), not a gate | Research A1: hard gates punish honest people |
| Visual tree | DAG Skill Tree (ReactFlow) | **Linear chapter stepper** | DAG is not a differentiator, saves 1 dev-day |
| Coding arena | Monaco + Piston + TDL | **CUT to roadmap** | Does not fit in 4 days |
| Anti-cheat | CSS `user-select:none` + blur + timer | **Focus Mode (MediaPipe ML, on-device) + auto-blur** | Research B1/B2: don't sell "anti-cheat", accessibility |
| Select-word | (none) | **Select word → ask AI (Socratic)** + suggested question | New flow feature |
| References | (none) | **PDF-RAG required + Google Search grounding optional** | New flow feature |
| File name | `docs/adrs/001-model-selection.md` | ADR 001-005 (see §11) | Adds ADRs for new decisions |

---

## 1. Executive Summary & Value Proposition

### 1.1 The "Anti-AI-Brain-Rot" Manifesto
In the Generative AI era, conventional learning platforms and course documents (PDFs/modules) are hitting an effectiveness crisis: **AI Brain Rot**. Students and engineers dump material into ChatGPT or NotebookLM to get instant summaries, instant quizzes, or code answers — with no reasoning process involved. As a result:
- Cognitive muscles weaken (*atrophy of critical thinking*).
- Long-term retention collapses.
- Illusory competence: feeling you understand because you read an AI summary, then collapsing the moment you hit a real *edge case*.

**Hard numbers (from primary research, used in the deck):**
- 95% of university students use AI (HEPI 2026).
- 67% of students say AI damages the way they think (RAND, Mar 2026).
- PISA 2025 lowest on record (OECD, Sep 2026).
- 72% of employers struggle to fill roles (ManpowerGroup 2026).
- An unguarded AI helper yields results 17% **worse**; an AI that refuses to answer = the damage disappears (arXiv 2606.26181, Jun 2026).

### 1.2 The Solution: Assay
**Assay** flips the AI paradigm from **"Passive Answer Dispenser"** to **"Active Socratic Enforcer & Interrogator"** with a **High-Friction, High-Reward** philosophy.

Assay hands out no free summaries. The system:
1. Captures the user's **learning intent** + the **role** they want to master + (optionally) a **supporting document**.
2. Generates a **topic checklist** in realtime from the intent + document content.
3. Builds a **chapter-based syllabus** from the document, enriched with relevant **external references**.
4. Locks the next chapter until the user passes the **interview quiz**.
5. Inside a chapter, the user can **select a word** to ask the AI — and the AI **asks back** (Socratic) instead of giving the answer.
6. Plants a **honeypot** (fictional concept) to catch users who copy-paste to an external LLM.
7. **Focus Mode** uses the camera + on-device ML to detect cheating → auto-blur.
8. Ends with a **per-chapter score + calibration gap** (the distance between "feeling you understand" and "actually understanding").

```
+--------------------------------------------------------------------------------+
|                          USER INTAKE (single screen)                           |
|  "What do you want to learn today?"  +  Role selector  +  PDF (optional)       |
|                         REALTIME CHECKLIST GENERATION                          |
|  Backend streams a topic checklist (role-based) from intent + PDF              |
|                               SYLLABUS SYNTHESIS                               |
|  AI chunks PDF -> chapters  +  pulls relevant refs (PDF-RAG + grounding)       |
|                              GATED CHAPTER READER                              |
|  Linear chapters, next LOCKED until the interview quiz is passed               |
|  Inside a chapter: select word -> ask AI (Socratic) + suggested questions      |
|                          INTERVIEW QUIZ (per chapter)                          |
|  - Honeypot (fictional concept)                                                |
|  - Focus Mode: camera + on-device ML, anti-cheat, auto-blur on cheating        |
|  - Calibration: user predicts own score before reveal                          |
|                                SCORING & REPORT                                |
|  Single score per chapter + Calibration Gap + integrity flags                  |
+--------------------------------------------------------------------------------+
```

### 1.3 Positioning (one sentence, use on deck slide 1)
> Every AI study tool answers your questions. Assay questions your answers.

---

## 2. Problem Statement & Competitive Positioning

### 2.1 Landscape
| Characteristic | NotebookLM / ChatGPT / Coursera | **Assay** |
|---|---|---|
| AI role | Library & passive assistant | Coach & reasoning examiner |
| Summaries | 1-click instant | **No summary button**. The user writes it |
| Material flow | Passive linear / free to skip | **Chapters locked** until the interview is passed |
| Integrity | No verification | **Honeypot + Focus Mode ML** |
| In-material interaction | None / separate chat | **Select word → ask AI (Socratic)** |
| Metrics | Multiple-choice score | **Reasoning score + calibration gap** |

### 2.2 Closest competitors & differentiation
- **Khanmigo / Google Learn About:** Socratic but *suggestive* — the user can just ask for the answer, there is no gatekeeping, no integrity detection, and no self-serve PDF upload. Assay = an *enforcement engine*, not a suggestive tutor.
- **Foreman (Track 5 competitor, AI Builder Cup 2026):** an "Honesty Canary" that tests the honesty of **AI agents**. Assay shares the same mechanism DNA, but tests **the honesty of humans who cheat with another AI**. A strong philosophical position — mention it in the deck.
- **Chopdesk (Track 1):** ships a heuristic offline fallback. Assay must have the same class of fallback.

### 2.3 Personas & market
- **Demo (B2C, human-facing):** students/developers who want to level up in a specific role (Frontend/Backend/Fullstack/etc.).
- **Story & monetization (B2B, institution-facing):** bootcamps & corporate L&D that can no longer trust grades/certificates/portfolios because of AI. Assay = a reasoning verification system.
- **JAPAC relevance:** a 9 million digital talent gap (World Bank); bootcamps with completion rates <15% and unverified competence.

---

## 3. Core User Flow (CANONICAL)

This is the official flow. All other documents (API-CONTRACTS, DEMO-SCRIPT, PITCH-DECK, TEAM-TASK) must follow this order.

### Step 1 — Intake Screen
One screen with three inputs:
1. **Intent:** free-text — *"What do you want to learn today?"*
2. **Role selector:** a fixed **role** list (seed) to pick from, e.g. `Frontend`, `Backend`, `Fullstack`, `DevOps`, `Data/ML`, `Mobile`, `QA/Test`, `Security`, `System Design`. If the user's intent is not in the seed → the backend automatically surfaces an **`Others`** option (free-text role).
3. **PDF upload (optional):** supporting document. May be empty.

### Step 2 — Realtime Checklist Generation
After submit, the backend generates a **topic checklist** in realtime based on: (a) intent, (b) selected role, (c) PDF content (if any). The frontend shows the checklist with checkboxes; the user may uncheck/check items before continuing. Checked items = syllabus material.

### Step 3 — Syllabus Synthesis
Backend AI integration:
- **Chunking:** split the PDF into several structured **syllabus chapters** (title, order, objective, time estimate).
- **Reference enrichment:** the AI pulls **relevant references** from additional sources to strengthen the learning outcome.
  - **PDF-RAG (required):** grounding inside the document, page-anchored. This is what makes honeypot claims verifiable.
  - **Google Search grounding (optional):** enabled for only 1-2 chapters, results **cached**, falls back to cache on API error.
- If there is **no PDF:** chapter content is generated by AI from the role taxonomy + grounding (chapters still work), with the source labelled.

### Step 4 — Gated Chapter Reader
- The frontend displays each **syllabus chapter**.
- **Guard:** the next chapter is **locked** until the user passes the current chapter's interview quiz.
- Inside the chapter page, the user can **select a word/sentence** from the content → a popover appears to **ask the AI**.
  - The AI answers **Socratically** (asks back / gives a hint), **not** with the direct answer.
  - If the user selects **several words**, the AI shows **suggested questions** relevant to that selection.

### Step 5 — Interview Quiz (per chapter)
Every chapter has an **interview quiz** with:
- **Honeypot:** the AI slips in a convincing fictional concept. Response classification → score dimension (not a gate).
- **Focus Mode (camera):** camera on + **on-device ML** (MediaPipe) detects signs of cheating (gaze/head-pose drift, more than 1 face, tab switch). If detected → **the page auto-blurs** + the event is flagged `assisted`.
  - **Privacy:** inference runs in the browser; **video is NOT sent to the server**, only boolean events.
- **Anti-cheat feature** (sold as a *focus & integrity signal*, not a "cannot be cheated" claim).
- **Calibration:** before the score is revealed, the user predicts their own score (0-100).

### Step 6 — Scoring & Final Report
- **Single score per chapter** (0-100), unlock threshold **≥ 75**.
- **Calibration gap** = |user prediction − actual score|. Used in the report, **not** as the unlock criterion.
- **Integrity flags** from Focus Mode + honeypot go into the report.
- **Final report:** cross-chapter scores + calibration gap trend + integrity log.

---

## 4. Feature Architecture & Functional Specifications

### 4.1 Pillar 1 — Intake & Role Selector
- **Intent input:** free-text, required. Min 3 words.
- **Role selector:** fixed seed (see §3 Step 1). If the intent matches no seed → the `Others` option appears automatically (backend detects via AI classify). The user can enter a custom role.
- **PDF optional:** PDF/raw text. If present, it becomes the primary content source.

### 4.2 Pillar 2 — Realtime Checklist Generation
- The backend generates the topic checklist from (intent + role + PDF content).
- The frontend renders in realtime (SSE or fast polling).
- The user can edit the selection (check/uncheck) before submitting.
- Selected items → become the basis of the syllabus chapters.

### 4.3 Pillar 3 — Syllabus Synthesis & Reference Enrichment
- **Chunking by structure:** Gemini splits the document into structured chapters (not blind 300-600 word chunks).
- **PDF-RAG:** every chapter has a page anchor into the document. Used for: (a) chapter content, (b) verifying honeypot claims ("this term appears on no page of your module").
- **Optional grounding:** Google Search grounding (Vertex AI) for 1-2 chapters. Results cached to Firestore.
- **No-PDF path:** chapters are generated from the role taxonomy + grounding, tagged `source: generated`.

### 4.4 Pillar 4 — Gated Chapter Reader & Inline Socratic Ask
- **Linear chapter stepper** (not a visual DAG). Per-chapter state: `LOCKED → ACTIVE_READING → INTERVIEW → SCORED → UNLOCKED/NEEDS_REVIEW`.
- **Guard:** `next` is locked by default; unlock only after the chapter score ≥ 75.
- **Select-word ask:** the user selects text in the chapter → popover.
  - **Socratic** mode: the AI asks back / gives a hint / points to the relevant page. It does **not** hand over the answer.
  - Several words selected → the AI offers **suggested questions**.
  - Every interaction is logged (for engagement metrics + audit).

### 4.5 Pillar 5 — Interview Quiz, Honeypot & Focus Mode
- **Multi-turn interview (2-3 rounds):** inferential/HOTS questions, adaptive follow-ups. Not "what is the definition of X".
- **Honeypot:**
  - Contextual fictional concepts (e.g. *"React Quantum Hook"*, *"Zero-Latency Mutex"*, *"bcSQL indexing"*).
  - Honeypot score dimensions (research A1):
    - `CRITICAL_REJECTION` (suspicious & accurate) → **+2**
    - `AI_HALLUCINATION_COPYPASTE` (long, confident, hallucinated) → **−2**
    - `UNVERIFIED_HONEST` ("I don't know") → **0** (honest, neutral)
    - `EVASIVE` (silent/vague, never touches it) → **−1**
  - **Not a gate.** The combined score still decides the unlock.
  - Deterministic catalog (ADR 002) + term variation so it cannot be memorized (ADR 005).
- **Focus Mode (camera):**
  - MediaPipe on-device: head-pose/gaze drift, face count, tab blur.
  - Detected → **auto-blur** the page + `assisted` flag.
  - Video **does not** leave the device; only boolean events go to the backend.
  - **Accessible Mode:** can be turned off (copy allowed, blur off, relaxed time) — the score is tagged `assisted`.
- **Response pressure timer:** measures the **user's thinking time** (starts once the question finishes streaming), not model wait time. The timer is a signal, not an auto-fail (research B3).

### 4.6 Pillar 6 — Scoring, Calibration & Report
- **Single score** per chapter 0-100 (concept + reasoning combined, computed deterministically from LLM classification — see ADR 002).
- **Unlock threshold:** ≥ 75.
- **Calibration:** user predicts score → reveal → `calibration_gap = |predicted − actual|`.
- **Report:** per-chapter scores, calibration gap trend, integrity log, honeypot verdict.
- **Appeal path:** the user can contest a score; the system reviews it (second verifier model) → tags it `uncertain` or revises.

---

## 5. Team Allocation (3 Developers)

Capacity: 3 people × 4 days ≈ 12 dev-days, effectively ~9.6 dev-days (integration overhead ~20%).
The new flow totals ≈ 11.25 dev-days + required research features ≈ 3.5 dev-days = **~14.75 dev-days**.
**That means cutting is MANDATORY**, not a choice. See §8.

```
+-------------------------------+--------------------------------+-------------------------------+
| DEV 1: FRONTEND & UX          | DEV 2: BACKEND & DATA          | DEV 3: AI ENGINE & EVAL       |
+-------------------------------+--------------------------------+-------------------------------+
| • Intake screen (intent+role) | • API server (FastAPI/Express) | • Gemini pipeline (chunking)  |
| • Checklist + chapter stepper | • PDF ingest & syllabus store  | • Socratic interviewer prompt |
| • Chapter reader + select-ask | • Session/chapter state machine| • Honeypot generator + class  |
| • Interview UI + Focus Mode   | • Focus-event ingest + fallback| • Calibration + verifier loop |
| • Calibration slider + report | • Cloud Run deploy + cache     | • eval/ harness + benchmarks  |
+-------------------------------+--------------------------------+-------------------------------+
```

---

## 6. Timeline to October 18 (HARD DEADLINE)

Today is Oct 14. 4 working days left + buffer.

| Date | Target | Key Output |
|---|---|---|
| **Oct 14 (Day 0)** | API contract + honeypot test | PRD v2 + API-CONTRACTS v2 agreed; empirical honeypot numbers (already in hand: 54%, n=80) |
| **Oct 15 (Day 1)** | Intake → checklist → syllabus | intake/checklist/syllabus endpoints live; PDF chunking + PDF-RAG |
| **Oct 16 (Day 2)** | Reader + interview + honeypot | Chapter reader + guard; multi-turn interview + honeypot classification |
| **Oct 17 (Day 3)** | Focus Mode + scoring + fallback | MediaPipe + auto-blur; calibration; final report; cached fallback |
| **Oct 18 (Day 4)** | Deploy + video + deck + submit | Cloud Run live; 3-minute video; deck PDF; **submit before 20:00 UTC+8** |

---

## 7. Technical Specifications

- **Stack:** Next.js 15 (App Router, TS, Tailwind) + FastAPI/Express; Gemini via Vertex AI / Google Gen AI SDK; Firestore (state + vector search).
- **Event hard requirement:** Google models only (Gemini/Gemma); `openai`/`anthropic`/`cohere` are banned in `package.json`. Deploy on Cloud Run/Firebase.
- **Structured output:** all grading uses JSON schema + function calling (ADR 002).
- **Model routing:** Gemini Flash = gates/chunking/honeypot/fast follow-ups; Gemini Pro = final reasoning evaluation + verifier (async).
- **Submission language:** UI, README, deck, video in **English**. Internal documents may stay in Indonesian.
- **Data contracts:** see `API-CONTRACTS.md` (v2.0.0) — the single source for endpoints & schemas.

---

## 8. Non-Goals (CUT from MVP) & Roadmap

| Dropped | Reason | Fate |
|---|---|---|
| Monaco + Piston + TDL (coding arena) | Does not fit in 4 days; not the wedge | Roadmap slide |
| Visual DAG Skill Tree (ReactFlow) | Not a differentiator; chapter stepper is free | Roadmap slide |
| Dual-metric (2 scores) | Single + calibration gap is cheaper & stronger | Replaced |
| Voice / Gemini Live | Latency + cost are risky in a live demo | Roadmap |
| Complex auth / multi-user | 1 demo user is enough | Roadmap |
| Multi-source input (video/audio) | PDF is enough for the demo | Roadmap |

**MANDATORY even in 4 days** (this is what lifts Technical Merit 40%): eval harness + numbers, verifier loop, calibration, cached fallback.

---

## 9. Winning Playbook (Rubric Mapping)

| Rubric | Weight | What earns it |
|---|---|---|
| Technical Merit & Gen AI | 40% | Eval harness + numbers, verifier loop, model routing, structured output, MediaPipe (Google stack), Cloud Run. **Not UI.** |
| Problem Alignment & Impact | 25% | Numbers in §1.1 (HEPI, RAND, PISA, Manpower) + B2B story |
| Innovation & Creativity | 25% | Pedagogical honeypot + calibration gap + select-word Socratic |
| UX & Solution Design | 10% | Accessible Mode + the calibration slider moment + clean design |

**Evidence numbers (from `reza-research/parts10/HASIL-TES-EMPIRIS.md`, DO NOT fabricate):**
- Honeypot hallucination rate: **54%** (n=80 calls, 4 models). Per model: gemini-flash-medium 75%, deepseek-v4-pro 70%, deepseek-v4-flash 45%, deepseek-v4.1-flash 25%.
- Trap effectiveness: **fictional_term 100%** (10 comply / 0 pushback / 2 error, n=12 valid), trap_number 58%, false_premise 25%, over_claim 25% (n=48).
- Verifier loop: 13/20 hallucinations caught (65%).
- Structured output valid JSON: 4/4 (100%).

> [!WARNING]
> **DO NOT use made-up numbers.** Deck v1 briefly claimed "91.3% / 640ms" and the demo script "sub-1.2s P95" — those numbers have no source. Every number in the submission must be traceable to `eval/` or `HASIL-TES-EMPIRIS.md`.

---

## 10. Risks & Mitigations

| # | Risk | Level | Mitigation |
|---|---|---|---|
| R1 | Scope too large (14.75 dev-days vs 9.6 capacity) | 🔴 CRITICAL | Cut §8; buffer on Day 4; add no new features |
| R2 | Honeypot fails (external LLM refuses to hallucinate) | 🟠 HIGH | Use empirical numbers; pin the most gullible model + the `fictional_term` trap (strongest, 100% at n=12) |
| R3 | LLM grading LLM = subjective | 🟠 HIGH | Deterministic classification (ADR 002) + verifier loop + appeal |
| R4 | Gemini down / rate limit during demo | 🟠 HIGH | `DEMO_MODE=cached` (2 scenarios: success + copy-paste caught) |
| R5 | "Anti-cheat" dismantled by the judges | 🟠 HIGH | Do not claim anti-cheat; sell "Focus Mode / integrity signal"; be honest that no system is cheat-proof |
| R6 | Accessibility (blur/copy-block) | 🟡 MEDIUM | Accessible Mode toggle; score tagged `assisted` |
| R7 | Honeypot false positives punish honest people | 🟡 MEDIUM | Honeypot = score dimension, not a gate |

**Q&A defense:** see `AUDIT.md` §10 (judge answer script).

---

## 11. Architecture Decision Records

| ADR | Title | Status |
|---|---|---|
| 001 | Model selection (Flash vs Pro) | Accepted |
| 002 | Deterministic hybrid guardrails vs pure LLM scoring | Accepted |
| 003 | Client-side ML (MediaPipe) vs server-side proctoring | Accepted |
| 004 | Role taxonomy seed + auto "Others" | Accepted |
| 005 | Honeypot: deterministic catalog + generative variation | Accepted |

Details in `docs/adrs/`.