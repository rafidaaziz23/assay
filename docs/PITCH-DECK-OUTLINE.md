# Pitch Deck Outline — Assay
## 10 Slides · 16:9 PDF · English

**Event:** AI Builder Cup 2026 (Google Cloud × Hack2skill, JAPAC)
**Track:** Track 4 — Media, Content & Digital Experiences (Adaptive Learning) — **single track**
**Submission deadline:** 18 October 2026, 23:59 UTC+8
**Team:** 3 developers
**Product name:** Assay *(codename repo: Active Learning Engine — `active-learning-engine/`)*

> **Number discipline:** every figure in this deck is traceable to `reza-research/parts10/HASIL-TES-EMPIRIS.md` or a named external study. No estimated, modelled, or illustrative metrics. See Slide 07.

---

### Slide 01 — Title

* **Title:** **Assay**
* **Subtitle:** The Active Socratic Learning Engine
* **Positioning line (hero, one sentence):** *Every AI study tool answers questions. Assay interrogates your answers.*
* **Badges:** Google Cloud Run · Gemini (Vertex AI) · MediaPipe on-device · AI Builder Cup 2026 · Track 4
* **Visual:** Split screen. Left: a chat box returning a confident answer. Right: Assay's interview screen asking the user to defend that same answer.
* **Speaker note:** Name the product once, state the positioning line once, move on. Do not explain the architecture here.

---

### Slide 02 — The Problem

**Headline:** AI made studying faster and understanding weaker.

* **Adoption is total:** 95% of students use AI for their studies (HEPI 2026).
* **Students know the cost:** 67% of pupils say AI harms their critical thinking (RAND, March 2026).
* **The trend line is down:** PISA 2025 recorded the lowest results on record (OECD, September 2026).
* **Employers cannot verify anyone:** 72% of employers struggle to fill roles (ManpowerGroup 2026).
* **The mechanism:** an unguarded AI helper leaves learners **17% worse off**; an AI that refuses to answer removes the damage (arXiv 2606.26181, June 2026).
* **The resulting failure mode:** *illusory competence* — the learner reads a generated summary, feels fluent, and collapses on the first edge case. Existing tools score the output. Nothing tests the reasoning behind it.
* **Visual:** Three stacked stat cards, then a single line: "Summary in, confidence out, understanding missing."

---

### Slide 03 — The Market Gap

**Headline:** Every incumbent optimises for the answer. None of them test the learner.

| | Coursera / Udemy | ChatGPT / NotebookLM | Khanmigo | **Assay** |
|---|---|---|---|---|
| Role of AI | Content delivery | Answer dispenser | Suggestive tutor | **Interrogator** |
| Summary button | Video, no synthesis | One click | Available | **None** |
| Progression | Free skip | Free skip | Free skip | **Locked until reasoning passes** |
| Integrity check | None | None | None | **Honeypot + Focus Mode** |
| In-material help | Forum | Separate chat | Chat | **Select text → Socratic ask** |
| Success metric | Completion | Fluency | Engagement | **Score + calibration gap** |

* **The gap:** no incumbent enforces cognitive friction. Khanmigo asks better questions but still lets the user ask for the answer and move on.
* **Visual:** The table, with the Assay column highlighted. Keep it readable — this is a 6-row comparison, not a feature dump.

---

### Slide 04 — The Solution

**Headline:** Assay does not hand out answers. It demands them.

**Three mechanisms:**

1. **Gated chapters.** The syllabus is split into chapters. The next chapter stays `LOCKED` until the current chapter's interview quiz is passed (score ≥ 75). There is no skip control and no summary button.
2. **Multi-turn Socratic interview + honeypot.** 2–3 rounds of inferential questions with adaptive follow-ups. The interviewer injects one plausible fictional concept per chapter. Answering it confidently with a fabricated justification is scored as copy-paste from an external LLM; rejecting it is scored as reasoning.
3. **Single score + calibration gap.** The learner predicts their own score before it is revealed. `calibration_gap = |predicted − actual|` becomes the headline metric of the final report, and it separates "felt ready" from "was ready".

* **Supporting, not headline:** PDF upload (optional), select-word Socratic ask, on-device focus signals.
* **Design principle:** high friction, high reward. The friction is the product.
* **Visual:** The canonical flow as a single vertical strip: Intake → Checklist → Syllabus → Gated Reader → Interview → Score + Gap.

---

### Slide 05 — What Makes It Different

**Headline:** Four things Khanmigo and NotebookLM do not do.

* **Enforcement, not suggestion.** Khanmigo can be asked for the answer. Assay's next chapter does not open until the reasoning passes. The gate is the differentiator.
* **Honeypot injection.** A fictional, contextually plausible term is placed inside the interview. The trap measures whether the learner (or their external LLM) verifies a claim or repeats it. *(This is the same DNA as a competitor's "honesty canary" — except that tests an AI agent's honesty, while Assay tests a human who is outsourcing to an AI.)*
* **Your own material.** Upload a PDF and the syllabus is grounded in it, page-anchored, so honeypot claims can be checked against the source. NotebookLM ingests documents but never interrogates you about them.
* **Calibration gap.** Every competitor reports a score. None report the distance between the learner's self-assessment and the measured result — the metric that exposes illusory competence.
* **Also:** select any word in a chapter to ask a question, and get a Socratic counter-question with a page citation instead of a direct answer.
* **Visual:** Two-column contrast, four rows, no more.

---

### Slide 06 — How It Works (Google Stack)

**Headline:** Gemini for reasoning, Cloud Run for delivery, MediaPipe for integrity — all on-device where it matters.

* **Client:** Next.js 15 (App Router, TypeScript, Tailwind).
* **API:** FastAPI on **Google Cloud Run**. REST + SSE for realtime checklist streaming.
* **Reasoning:** Gemini via **Vertex AI / Google Gen AI SDK**. Flash handles chunking, honeypot classification and fast follow-ups; Pro handles final reasoning evaluation and the async verifier.
* **Grounding:** PDF-RAG (mandatory, page-anchored) + optional Google Search grounding on 1–2 chapters, cached to Firestore.
* **State:** Firestore, with the chapter state machine `LOCKED → ACTIVE_READING → INTERVIEW → SCORED → UNLOCKED / NEEDS_REVIEW`.
* **Integrity:** **MediaPipe on-device** — gaze/head-pose drift, multiple faces, tab blur. Video never leaves the browser; only boolean events are transmitted (ADR 003). Focus Mode is sold as an *integrity signal*, not as an anti-cheat guarantee.
* **Reliability:** `DEMO_MODE=cached` replays two pre-recorded scenarios (critical rejection / copy-paste caught) if Gemini returns 429/500/503.
* **Constraint compliance:** Gemini/Gemma only. No `openai`, `anthropic`, or `cohere` in `package.json`.
* **Visual:** One architecture diagram, left to right. Keep it to six boxes.

---

### Slide 07 — Measured Results

**Headline:** We tested the honeypot against real models before claiming it works.

All figures below are measured, not modelled. Source: `reza-research/parts10/HASIL-TES-EMPIRIS.md` (2026-10-14, local gateway, 5 workers, raw responses retained in `results/*.jsonl`, classified by transparent regex heuristics rather than an LLM judge).

**Honeypot hallucination rate — do external LLMs invent a fictional concept?**
**54%** across **n = 80** calls and 4 models. The models fabricate a confident definition in **43** of 80 calls; **29** refuse.

| Model | Hallucination rate |
|---|---|
| gemini-3.8-flash-medium | 75% |
| deepseek-v4-pro | 70% |
| deepseek-v4-flash | 45% |
| deepseek-v4.1-flash | 25% |

**Trap effectiveness by type — which trap catches a copy-paste?** (n = 48 classified calls; 58 records are logged in `results/p2_traps.jsonl` — the report and the raw log disagree on the error count, so we cite the classified subset)

| Trap | Effectiveness |
|---|---|
| fictional_term | **100%** (10 comply, 0 pushback, 2 error) |
| trap_number | 58% |
| false_premise | 25% |
| over_claim | 25% |

Effectiveness is computed on valid records only; errored calls are excluded rather than counted as pushback. Note that `fictional_term` sits at the ceiling of this sample, which is a small-n result (12 records) and should be read as "this trap type works", not as a precise rate.

**Verifier loop — can a second model catch a hallucination?** **13 of 20 caught (65%)**; 4 missed, 3 inconclusive. A second model is useful but not sufficient, which is why the verifier is paired with deterministic classification (ADR 002) and a user appeal path.

**Structured output — does the scoring schema hold?** **4 of 4 valid JSON (100%)**, so scoring never falls back to free-text parsing.

**Judge-model discrimination (P3):** the same judge scored correct answers 92–95 and wrong answers 10–20, a gap of 75–85 points. The evaluator is not sycophantic on this sample.

**What we do not claim:**
* No application latency figure is claimed. The only latency we measured (13–34 s per call, 25 s average) is a probe against a local gateway proxy and reflects the test harness, not the product.
* These are initial measurements. The methodology note in the source states that final deck figures need manual spot-checks on a sample; we say so rather than rounding upward.
* **Log reconciliation.** The raw logs hold 84 honeypot records and 58 trap records, while the report classifies 80 and 48 respectively. The difference is retried calls that errored at the gateway (7 and 10 records). The report's classified counts are the ones cited above. Per-model honeypot rates are computed on 20 classified calls per model, so the denominators are stable; the small-n trap result for `fictional_term` (12 records) is the weakest number in this deck and we label it as such on the slide.
* Honeypot is a **score dimension** (+2 critical rejection, −2 hallucination copy-paste, 0 honest "I don't know", −1 evasive), not a hard gate — a hard gate punishes honest learners (ADR 002).

**Visual:** Three stat blocks — 54% hallucination, 65% verifier catch, 4/4 schema validity — above the two small tables, with the source line printed small but legible. Judges who check will find the file.

---

### Slide 08 — Market: TAM / SAM / SOM

**Headline:** Sell the verification layer to institutions that can no longer trust their own certificates.

**Beachhead:** B2B, two segments in Southeast Asia — **tech bootcamps** and **enterprise engineering L&D / onboarding**.

| Layer | Definition | Basis |
|---|---|---|
| **TAM** | All digital-skills education and corporate L&D in JAPAC | JAPAC faces a **9-million digital talent gap** (World Bank) |
| **SAM** | Bootcamps and enterprise engineering L&D in SEA that issue a competence credential | **72%** of employers struggle to fill roles (ManpowerGroup 2026) — credential trust is the bottleneck |
| **SOM** | 12-month beachhead: a small number of bootcamp cohorts plus 2–3 enterprise pilots | Bottom-up: seats × price per seat, to be filled from named pipeline conversations |

> **Pricing and revenue figures are deliberately absent.** The previous draft of this deck carried an unsourced "$120M SOM" and a "70% grading-overhead reduction". Neither had a source. We would rather show an empty cell than a made-up one — and we will fill it with the pilot pipeline before submission.

* **Why institutions pay:** their completion certificates and graduate portfolios are no longer evidence of anything, because AI can produce both. Assay produces a reasoning transcript with a calibration gap and an integrity log attached.
* **Why students use it:** the free B2C flow — intent, role, optional PDF — is the demo and the top of the funnel.
* **Unit economics to state on the slide once sourced:** seats per cohort, price per seat per term, and pilot-to-contract conversion.
* **Visual:** Three nested rings (TAM/SAM/SOM) with the SOM ring labelled "bottom-up, sourced".

---

### Slide 09 — Roadmap

**Headline:** Three phases. Phase 1 is the only thing we are building before 18 October.

**Phase 1 — MVP (now, through 18 October 2026)**
* Intent + role intake, realtime checklist, PDF-optional syllabus synthesis.
* Gated chapter reader with select-word Socratic ask.
* Multi-turn interview with honeypot classification and deterministic scoring.
* Calibration slider, final report, appeal path.
* MediaPipe Focus Mode (on-device), `DEMO_MODE=cached` fallback, Cloud Run deployment.
* Cut from MVP and moved here deliberately: coding arena (Monaco + Piston), DAG skill tree, voice/Gemini Live, multi-user auth, video/audio input.

**Phase 2 — Post-hackathon (Q1 2027)**
* Multimodal vision: diagram, chart and whiteboard verification.
* IDE integration (VS Code / JetBrains) so onboarding happens where the engineer already works.
* Voice interview rounds.

**Phase 3 — Enterprise (Q2 2027)**
* Multi-tenant org accounts, SSO, cohort analytics dashboards.
* Per-team competency maps and hiring-signal exports.
* Compliance-grade audit trail for the integrity log.

* **Visual:** Horizontal timeline, three blocks, MVP block highlighted. Show the cut list as small grey text under Phase 1 — it demonstrates scope discipline rather than hiding it.

---

### Slide 10 — Team & Call to Action

**Headline:** Three developers, four days, one track.

* **Team:** 3 developers — frontend/UX, backend & data, AI engine & evaluation.
  * Dev 1 — intake, checklist, chapter stepper, reader + select-ask, interview UI, Focus Mode, calibration, report.
  * Dev 2 — API server, PDF ingest, session/chapter state machine, focus-event ingest, Cloud Run deploy, cache.
  * Dev 3 — Gemini pipeline, Socratic interviewer prompt, honeypot generator + classifier, calibration + verifier loop, eval harness.
* **Engineering decisions documented:** ADR 001–005 in `docs/adrs/` — model selection (Flash vs Pro), deterministic hybrid guardrails vs unbounded LLM scoring, client-side MediaPipe vs server-side proctoring, role taxonomy with auto "Others", honeypot catalog + generative variation.
* **Built on the required stack:** Gemini/Gemma only, deployed on Cloud Run.
* **Try it:** `https://<cloud-run-url>` — live demo, plus `DEMO_MODE=cached` if the network fails on stage.
* **Visual:** Three team cards, one line of credentials each, then the URL large enough to read from the back of the room.

---

## Appendix — Number Provenance

Every metric used in this deck, with its source. If a number is not in this table, it does not belong in the deck.

| Metric | Value | Source |
|---|---|---|
| Honeypot hallucination rate (all models) | 54% (n = 80) | `HASIL-TES-EMPIRIS.md` P1 |
| gemini-3.8-flash-medium | 75% | P1 |
| deepseek-v4-pro | 70% | P1 |
| deepseek-v4-flash | 45% | P1 |
| deepseek-v4.1-flash | 25% | P1 |
| Trap effectiveness — fictional_term | 100% (10/10 valid) | P2 |
| Trap effectiveness — trap_number | 58% | P2 |
| Trap effectiveness — false_premise | 25% | P2 |
| Trap effectiveness — over_claim | 25% | P2 |
| Verifier loop catch rate | 13/20 (65%) | P4 |
| Structured output valid JSON | 4/4 (100%) | P5 |
| Judge discrimination gap | 75–85 pts | P3 |
| Students using AI | 95% | HEPI 2026 |
| Pupils reporting AI harms critical thinking | 67% | RAND, March 2026 |
| PISA 2025 lowest on record | — | OECD, September 2026 |
| Employers struggling to fill roles | 72% | ManpowerGroup 2026 |
| JAPAC digital talent gap | 9 million | World Bank |
| Unguarded AI helper penalty | 17% worse | arXiv 2606.26181, June 2026 |

**Removed from the previous version of this deck:** "Honeypot Hallucination Trap Rate: 91.3% capture rate across 30 tested synthetic concepts" and "Mean Latency: 640 ms across 50 simulated Socratic evaluation turns". Both were unsourced and are not reproducible from any test artifact in this repository.
