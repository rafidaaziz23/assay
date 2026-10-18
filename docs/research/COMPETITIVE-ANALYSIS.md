# Intel & Deep Research: AI Builder Cup 2026 Competitor Landscape

**Competitive Intelligence Document — v2.0.0**
**Product:** **Assay** — The Active Socratic Learning Engine
*(repo codename: Active Learning Engine — `active-learning-engine/`)*
**Event:** Google Cloud x Hack2skill — AI Builder Cup 2026 (JAPAC Regional)
**Track:** **Track 4 — Media, Content & Digital Experiences (Adaptive Learning) — ONE TRACK ONLY**
**Submission Target:** **October 18, 2026, 23:59 UTC+8** (HARD DEADLINE)
**Research Focus:** Active competitors in 2026, profiles of past winners (Gen AI Exchange), and vulnerability assessment

> **Changelog from v1 of this document:** product name CogniForge → **Assay**; Track 4 **and** Track 5 → **Track 4 only** (rule: 1 team = 1 track); deadline 19 → **October 18, 2026**; old flow (mandatory PDF upload → 300-600 word chunks → concept node) → **flow v2** (intent + role + optional PDF → realtime checklist → chapter syllabus); dual-metric → **single score + calibration gap**; DAG Skill Tree → **linear chapter stepper**; Monaco/Piston coding arena → **CUT to roadmap**; honeypot from hard gate → **score dimension**.
> Every number in this document comes from `reza-research/parts10/HASIL-TES-EMPIRIS.md` or a named external study. No invented numbers.

---

## 1. Direct Competitor Map for AI Builder Cup 2026 (Live Reconnaissance)

From a survey of public AI Builder Cup 2026 participant repositories, there are **two high-caliber competitors** that have already built aggressively and set a high bar. Both are in tracks different from Assay — so they are not head-to-head opponents, but they are the **quality benchmark** against which judges will compare.

```
┌───────────────────────────────┬─────────────────────────────────┬───────────────────────────────┐
│                                 ACTIVE COMPETITOR LANDSCAPE 2026                                │
├───────────────────────────────┼─────────────────────────────────┼───────────────────────────────┤
│ PARAMETER                     │ FOREMAN (@arnavbee)             │ CHOP / CHOPDESK (@CrimsonS)   │
├───────────────────────────────┼─────────────────────────────────┼───────────────────────────────┤
│ Track                         │ Track 5: Future of Work         │ Track 1: BFSI                 │
│ Tagline / Problem             │ "Agent that hires & vets agents"│ "Don't pay until it's chopped"│
│                               │ Enterprise agent governance     │ Invoice fraud & vendor-swap   │
│ Tech Stack                    │ Python, ADK 2.x, A2A Protocol,  │ Next.js 15, TypeScript,       │
│                               │ Gemini 2.5 Pro/Flash, Cloud Run │ Gemini 2.5 Flash, Cloud Run SG│
│ Repo Size                     │ 43 files                        │ 63 files                      │
│ Fatal Strength                │ • Honesty canary & test probes  │ • Real JAPAC local problem    │
│                               │ • Demo has a rejected "villain" │ • Heuristic offline fallback  │
│                               │ • Per-second video script, tight│ • /brief route auto-generate  │
│ Weak Point                    │ Problem too abstract/futuristic,│ No execution sandbox code,    │
│                               │ current economic value not real │ very narrow B2B APAC segment  │
└───────────────────────────────┴─────────────────────────────────┴───────────────────────────────┘
```

### Deep Dive 1: FOREMAN (The Apex Threat in the Enterprise Track)

- **Architecture:** *Agent-to-Agent (A2A)* protocol with the cycle:
  `Plan → Discover → Vet → Delegate → Verify → Deliver (+ hash-chained audit ledger)`
- **Demo Trick That Captivates Judges:** they built **"Villain Agents"** inside the demo registry:
  1. `quickfix` — a lazy agent that answers *"Done"* to every task without executing.
  2. `oracle` — an agent that always answers very convincingly but is 100% hallucinating.
  *On camera, Foreman catches and rejects both agents using an **"Honesty Canary"** — a question whose answer deliberately does not exist.*
- **Reliability:** `FOREMAN_FAKE_LLM=1` for development without an API key. The demo never dies.
- **Lesson for Assay:**
  Assay's **honeypot** mechanism shares the same DNA as Foreman's **Honesty Canary**. The difference is one sentence: **Foreman tests the honesty of AI agents; Assay tests the honesty of humans cheating with another AI.** This is a strong philosophical position — state it explicitly in the deck and in Q&A. If judges have already seen Foreman, they will immediately recognize the pattern and score Assay as the human-side mirror of the same mechanism.

### Deep Dive 2: CHOPDESK (The Localization Master in BFSI)

- **Real Problem:** purchasing staff at Southeast Asian importer SMEs (Singapore, Penang, etc.) still pay invoices worth hundreds of millions via WhatsApp and PDF email, where vendor bank accounts are prone to forgery.
- **Engineering Trick:** **heuristic fallback.** If the Gemini API hits an HTTP 429 rate limit or the connection drops, the app automatically switches to local vendor graph analysis with the message: *"(Gemini unreachable — local vendor graph used.)"*. **Their demo has 0% blank risk.**
- **Lesson for Assay:**
  Assay **must** have the same class of fallback: `DEMO_MODE=cached` (env) **or** the header `x-demo-mode: cached`, plus an automatic trigger when Gemini returns 429/500/503. Two pre-cached scenarios are required: **success flow** (`CRITICAL_REJECTION`, high score, chapter unlock) and **caught flow** (`AI_HALLUCINATION_COPYPASTE`, score drops, integrity flag). The `LOCAL_DETERMINISTIC_CACHE` banner can be shown on camera — it is a feature, not a glitch.

---

## 2. DNA Teardown of Past Google Cloud Hackathon Winners (Historical Champions)

Analyzing the official *Google Cloud Gen AI Exchange* winners and APAC regional winners yields a blueprint of what **Google Cloud judges actually score**:

| Winner & Year | Category / Track | Key Tech Stack | The Winning Factor |
|---|---|---|---|
| **Padayon Ko**<br>*(APAC 1st Place 2024)* | EdTech / Social Impact (Philippines) | Gemini API, Google Chirp STT, Synthesize TTS, Flask, Cloud Run | **`benchmarks/` folder:** a 100-request latency test report (mean 2850 ms, SD 436 ms). Backed by TAM/SAM/SOM notebooks and real adoption by 500 students in Lapu-Lapu City. |
| **Savour AI**<br>*(APAC 2nd Place 2024)* | FoodTech (Australia) | Gemini 2.0 Flash/Pro, LangGraph, MongoDB Atlas, Streamlit | **Formal ADRs:** 4 decision documents, with the courage to reject Google Agent Builder ("too rigid") and choose LangGraph. Shipped only 3 MVP features, the rest as roadmap. |
| **Team Skippers**<br>*(Pro 1st Place 2025)* | Future of Work (Enterprise QA) | Gemini Pro, Automated Test Framework | Linked medical regulatory specifications to automated unit test execution. Solved a compliance problem worth billions of rupiah. |
| **May The Agents Be With You**<br>*(Pro 1st Place 2025)* | Manufacturing Operations | Multi-Agent Orchestration, Industrial IoT | Worked directly with JK Cement to autonomously optimize energy consumption at a cement plant. |
| **KalaSarthi**<br>*(Featured Finalist 2025)* | Retail / Artisans (India) | Next.js 15, Gemini 2.0 Flash + Nano, Firebase, Redis | **3-Tier Offline-First Architecture:** `Gemini Flash (Online)` → `Gemini Nano (On-Device)` → `SimpleOfflineAI (Fallback)`. Resilient without an internet connection. |
| **YouthMind**<br>*(Student 1st Place 2025)* | Mental Health | Vanilla HTML/JS, 12 audio mp3s (18 files, NO README) | **Storytelling & Empathy:** lines of code mattered less than the strength of the 3-minute pitch delivery. |

**Patterns relevant to Assay:**

- Padayon Ko won with a **`benchmarks/` folder** — Assay has `eval/` + `benchmarks/` with empirical honeypot numbers (n=80). This is exactly the same kind of evidence.
- Savour won with **ADRs + scope discipline** — Assay has ADRs 001-005 and an explicit cut list (§8 PRD). Do not hide the cut list; present it as proof of discipline.
- KalaSarthi won with **layered fallbacks** — Assay has `DEMO_MODE=cached` + grounding cache + deterministic honeypot catalog.
- YouthMind won with **delivery** — Assay's 3-minute video is already scripted per second. The script is written before recording, not after.

---

## 3. Google Cloud Hackathon Myths vs Facts

```
┌──────────────────────────────────────────────┬──────────────────────────────────────────────┐
│ COMMON PARTICIPANT MYTH                      │ EMPIRICAL FACT AT THE JUDGES' TABLE          │
├──────────────────────────────────────────────┼──────────────────────────────────────────────┤
│ "You must build a lavish Next.js UI."        │ Savour placed 2nd using plain Streamlit.     │
│                                              │ YouthMind won using bare HTML.               │
│ "You must fine-tune your own model."         │ 100% of winners used pre-trained Gemini.     │
│ "You must build 10-15 comprehensive          │ Shipping 10 half-baked features = drop. 3    │
│ features."                                   │ features working perfectly = winner.         │
│ "You must use every Google AI product."      │ Savour rejected Agent Builder via ADR and    │
│                                              │ still won. What matters: Gemini + Cloud Run  │
│                                              │ must run.                                    │
│ "A tidy repo is a guaranteed win."           │ YouthMind won 1st with no README; what       │
│                                              │ mattered was the 3-minute pitch video &      │
│                                              │ working live demo.                           │
│ "More tracks = better odds of winning."      │ 1 team = 1 track. Assay takes Track 4 only.  │
└──────────────────────────────────────────────┴──────────────────────────────────────────────┘
```

---

## 4. Competitor Weak Point Analysis (Vulnerability Assessment)

How can Assay beat competitors in other tracks and similar participants?

### 1. Most Participants Fall into the "AI Helper Bias"

- **Opponent Weakness:** most participants build an all-helpful bot (*"Ask me anything, I'll summarize it, I'll write the code for you"*).
- **Assay's Attack:** Assay is the only one taking the **AI Adversarial / Enforcer** position. What it attacks is a real phenomenon: *"Generative AI is making a new generation of engineers lazy about critical thinking."* The contrast is extreme and immediately memorable to judges.

### 2. Track 5 Competitor (Foreman) Is Too Conceptual

- **Foreman's Weakness:** *"Agents hiring agents with Ed25519 signatures"* is a solution for the world 5 years from now, when companies already have thousands of autonomous agents. No JAPAC company needs that today.
- **Assay's Advantage (Track 4):** the degradation of student/developer understanding caused by AI is happening **today, this hour**, across every bootcamp and university in Southeast Asia. Immediate market relevance.
- **Important note:** because Assay is now **Track 4 only**, Foreman is no longer a direct opponent — it becomes a **quality reference and narrative source** ("the same mechanism, the human side").

### 3. Closest Competitor in Track 4: Commercial Incumbents, Not Participants

- **Khanmigo / Google Learn About:** Socratic but *suggestive*. Users can ask for the answer directly, there is no gatekeeping, no integrity detection, and no self-service PDF upload. Assay = an *enforcement engine*, not a suggestive tutor.
- **NotebookLM / ChatGPT:** a library and an answer dispenser. NotebookLM swallows documents but never interrogates their owner. Assay reverses the direction of the question.
- **Coursera / Udemy:** progress based on content completion, freely skippable, zero verification of reasoning.

### 4. The Forbidden Dependency Trap (The Disqualification Trap)

- Research found that a participant such as *Artifind* did not pass because they wrote *"[OI]/Claude for text generation"* in the README.
- The *Padayon Ko* repository once leaked an active Facebook token in `.env.example`.
- Another participant committed `.env`, placed build output `dist/` (90 of 157 files), and was inconsistent about their own product name (README "LegalEase AI" vs document "LegalMind AI").
- **Assay Security Procedure:**
  - `package.json` / `requirements.txt` 100% clean of the `openai`, `anthropic`, `cohere` packages.
  - Only `@google/genai` or `@google/generative-ai`; Google models only (Gemini/Gemma).
  - Deployment **must** be on Cloud Run (or Firebase).
  - `.env.example` uses dummy credentials; `.env` never enters the repo.
  - **One product name across all artifacts: Assay.** The repo codename `active-learning-engine/` may stay, but the UI, README, deck, and video all say **Assay**.

---

## 5. Comparison Matrix: Assay vs Key Competitors

| Evaluation Dimension | Foreman (`arnavbee`) | Chopdesk (`CrimsonSithria`) | Khanmigo / NotebookLM | **Assay (Our Project)** |
|---|---|---|---|---|
| **Track** | Track 5 (Future of Work) | Track 1 (BFSI) | Commercial education market | **Track 4 (Media, Content & Digital Experiences) — the only track** |
| **AI Role** | Agent auditor | Payment verifier | Suggestive tutor / library | **Interrogator — questions the user's answers** |
| **Core Moat** | A2A Protocol & Ed25519 | Vendor Lookalike Graph | Knowledge base + Socratic chat | **Honeypot injection + gated chapter + calibration gap** |
| **"Honesty Test" Mechanism** | "Honesty Canary" — a nonexistent fact, for AI agents | Vendor master match | None | **Honeypot — a fictional concept, for humans cheating with AI** |
| **"Villain" Demo** | Fake agents `quickfix` & `oracle` | Fictional CEO-fraud invoice | None (always passive) | **A student copy-pasting answers from an external LLM — caught red-handed** |
| **Integrity** | Hash-chained audit ledger | Vendor master match | Zero (easy to cheat) | **Honeypot score dimension + Focus Mode (MediaPipe on-device)** |
| **Fallback when the API is down** | `FOREMAN_FAKE_LLM=1` | Local heuristic vendor graph | N/A | **`DEMO_MODE=cached` + header `x-demo-mode: cached` + grounding cache** |
| **Main Weakness** | Market not ready, value not real today | Scope too narrow | Encourages cognitive laziness | Needs discipline to limit scope to 4 days |
| **Win Probability** | Very high (Track 5) | High (Track 1) | N/A (incumbent) | **Very high (Track 4)** |

### 5.1 Assay vs Incumbent Differentiation Matrix (Flow v2)

| | Coursera / Udemy | ChatGPT / NotebookLM | Khanmigo | **Assay** |
|---|---|---|---|---|
| AI role | Content deliverer | Answer dispenser | Suggestive tutor | **Interrogator** |
| Summary button | Video, no synthesis | One click | Available | **None** |
| Progression | Free skip | Free skip | Free skip | **Locked until reasoning passes (score ≥ 75)** |
| Integrity check | None | None | None | **Honeypot + Focus Mode** |
| Help inside the material | Forum | Separate chat | Chat | **Select word → ask AI (Socratic)** |
| Bring your own material | Vendor modules | Document upload | No | **Optional PDF, page-anchored (PDF-RAG)** |
| Success metric | Completion | Fluency | Engagement | **Score + calibration gap** |

---

## 6. What's New in Assay v2 (and Why It Isn't Just More Features)

This is not a feature list. This is what separates Assay v2 from v1 and from incumbents, in flow order:

1. **Intent-first intake, not upload-first.** The user starts from a learning intent + role (Frontend/Backend/Fullstack/DevOps/Data-ML/Mobile/QA-Test/Security/System Design), with an **`Others`** option appearing automatically when the intent matches no seed (ADR 004). PDF is **optional** — without a PDF, chapters are generated from the role taxonomy and tagged `source: generated`. Other incumbents demand a document first.
2. **A realtime checklist the user can edit.** Items stream via SSE (`checklist.partial`), each tagged `document` / `role_taxonomy` / `grounded_external`. Unchecked items **never become chapters**. The study plan belongs to the user, not the model.
3. **Mandatory PDF-RAG + optional Google Search grounding.** Every chapter has a page-anchor to the document. This is what makes honeypot claims verifiable ("this term does not appear on any page of your module"). External grounding is limited to 1-2 chapters and **cached**, so the demo does not depend on the network.
4. **Inline select-word → ask AI (Socratic).** The user selects a word or phrase inside a chapter → popover. The AI **asks back / gives a hint / points to the page**, rather than giving a definition. The field `gave_direct_answer: false` appears in the response panel. Selecting several words → **suggested questions** appear. This is the "anti brain-rot" thesis in its smallest interaction form.
5. **Per-chapter interview quiz + honeypot as a score dimension.** 2-3 rounds of inferential questions (not "what is the definition of X") with adaptive follow-ups. One fictional concept is slipped into each chapter. Deterministic classification → score: **`CRITICAL_REJECTION` +2**, **`AI_HALLUCINATION_COPYPASTE` −2**, **`UNVERIFIED_HONEST` 0**, **`EVASIVE` −1**. **Not a gate** — unlock is still decided by `chapter_score >= 75`. A hard gate would punish honest learners who say "I don't know" (ADR 002).
6. **Calibration gap.** Before the score is revealed, the user predicts their own score. `calibration_gap = |predicted − actual|` becomes the report's primary metric. Every competitor reports a score; none reports the **distance between "feeling ready" and "actually ready"**. This is the metric that exposes *illusory competence*.
7. **On-device Focus Mode (MediaPipe) + auto-blur.** Gaze/head-pose drift, face count > 1, tab blur — all inference in the browser. Video **never leaves the device**; only boolean events are sent (`video_transmitted: false`, ADR 003). On detection → the page **auto-blurs** + an `assisted` flag. **Accessible Mode** can disable the camera → `assisted_unverified`, and the score is still computed. Marketed as an *integrity signal*, not a claim that "cheating is impossible".

---

## 7. What Was CUT from the MVP (Moved to Roadmap — Show It, Don't Hide It)

| Cut from MVP | Reason | Fate |
|---|---|---|
| **Coding arena (Monaco + Piston + TDL)** | Does not fit in 4 days; not the differentiation wedge | Roadmap Phase 2 |
| **Visual DAG Skill Tree (ReactFlow)** | Not a differentiator; the linear chapter stepper is free and clearer | Roadmap Phase 2 |
| **Dual-metric (2 separate scores)** | Single score + calibration gap is cheaper and demos stronger | Replaced |
| Voice / Gemini Live | Latency + cost are risky in a live demo | Roadmap Phase 2 |
| Complex auth / multi-user | A 1-user demo is enough | Roadmap Phase 3 |
| Multi-source input (video/audio) | PDF is enough for the demo | Roadmap Phase 2 |

**What MUST exist even with 4 days** (this is what lifts Technical Merit 40%): eval harness + numbers, verifier loop, calibration, cached fallback, on-device Focus Mode.

---

## 8. The 5 Golden Components Formula for a Winning Submission

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│              THE 5 GOLDEN COMPONENTS OF A WINNING SUBMISSION (CHECKLIST)               │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ 1. `benchmarks/` + `eval/`                                                             │
│    A harness that runs the honeypot & trap suite against Google models, with raw       │
│    output stored (JSONL) and deterministic classification — not an LLM judge.          │
│    Numbers used: 54% hallucination (n=80), fictional_term 100% (n=12 valid) /          │
│    trap_number 58% (n=48), verifier 13/20 (65%), structured JSON 4/4.                  │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ 2. `docs/adrs/` — ADR 001 through 005                                                  │
│    001 model selection (Flash vs Pro) · 002 deterministic hybrid guardrails vs pure    │
│    LLM scoring · 003 client-side MediaPipe vs server-side proctoring · 004 role        │
│    taxonomy seed + auto "Others" · 005 deterministic honeypot catalog + generative     │
│    variation. Also document the REJECTED alternatives, not just the decisions made.    │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ 3. Offline fallback (`DEMO_MODE=cached`)                                               │
│    Env `DEMO_MODE=cached` OR header `x-demo-mode: cached` OR Gemini 429/500/503.       │
│    Two required scenarios: success flow (CRITICAL_REJECTION, unlock) and caught flow   │
│    (AI_HALLUCINATION_COPYPASTE, integrity flag). External grounding is cached too.     │
│    The video and live URL must not be blank when judges review.                        │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ 4. 3-minute demo video (180s, hard cap) — script written first                         │
│    00:00-00:20  Problem: 95% use AI, 67% say it damages how they think.                │
│    00:20-00:50  Intake: intent + role (+ optional PDF, then repeated with PDF).        │
│    00:50-01:15  Realtime streaming checklist, user unchecks one item.                  │
│    01:15-01:40  Syllabus + page-anchor + grounded references (cached: true).           │
│    01:40-02:05  Reader locked + select word → AI asks back.                            │
│    02:05-02:45  GOLDEN MOMENT: copy-paste to external LLM → honeypot −2; reject → +2.  │
│                 Focus Mode detects → auto-blur. Calibration slider filled in.          │
│    02:45-03:00  Reveal score 88, threshold 75, calibration gap 2, report + appeal.     │
│    No logo, no team intro. The first frame is the problem.                             │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ 5. Pitch deck 10 slides, English, PDF                                                  │
│    Includes the competitor table (this document §5), bottom-up TAM/SAM/SOM, 3-phase    │
│    roadmap with the cut list shown as scope discipline, and an appendix of number      │
│    provenance. Every number must be traceable. If it is not in the provenance          │
│    table, it does not go in the deck.                                                  │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 9. Evidence Numbers (Single Source, Never Invented)

Source: `reza-research/parts10/HASIL-TES-EMPIRIS.md` — October 14, 2026, local gateway, 5 workers, raw responses in `results/*.jsonl`, heuristic regex classification (transparent, not an LLM judge).

| Claim | Number | Sample |
|---|---|---|
| Honeypot hallucination rate (all models) | **54%** | n = 80 calls, 4 models |
| — gemini-3.8-flash-medium | 75% | 20 calls |
| — deepseek-v4-pro | 70% | 20 calls |
| — deepseek-v4-flash | 45% | 20 calls |
| — deepseek-v4.1-flash | 25% | 20 calls |
| Trap effectiveness: fictional_term | **100%** (10 comply / 0 pushback / 2 error) | n = 12 valid |
| Trap effectiveness: trap_number | 58% | n = 48 |
| Trap effectiveness: false_premise | 25% | n = 48 |
| Trap effectiveness: over_claim | 25% | n = 48 |
| Verifier loop catches hallucinations | 13/20 (65%) | 20 hallucinated answers |
| Structured output valid JSON | 4/4 (100%) | 4 schema calls |

**What is not claimed:**

- **No latency numbers** are used in the deck or video. What the harness measured were probes to a local gateway (average 25s), which reflects the harness, not the product.
- The P3 numbers (judge discrimination, 75-85 point gap) exist in the source but are not used as a product claim.
- Deck v1 once wrote "91.3% capture rate" and "640 ms latency"; demo script v1 once wrote "sub-1.2s P95". **All three are unsourced and must never reappear** in any form.
- The honeypot is a **score dimension**, not a hard gate.

---

## 10. Pre-Submission Checklist (October 18, 2026)

- [ ] **Name consistency:** no leftover "CogniForge" strings in the README, UI, deck, video, or code comments. Everything says **Assay**.
- [ ] **Track statement:** the deck and submission form mention **Track 4** only, with no mention of Track 5.
- [ ] **Dependency audit:** no `openai` / `anthropic` / `cohere` in `package.json` or `requirements.txt`; Google packages only.
- [ ] **Deploy:** Cloud Run live and accessible to judges, with `DEMO_MODE=cached` standing by.
- [ ] **Secret hygiene:** `.env` is not committed; `.env.example` contains dummies.
- [ ] **No build output:** `dist/` / `build/` / `node_modules` are not in the repo.
- [ ] **Repo contains:** `benchmarks/`, `eval/`, `docs/adrs/001-005`, architecture diagrams, competitor table + differentiation rationale.
- [ ] **Clear separation of "shipped" vs "roadmap":** the cut list (§7) is shown, not hidden.
- [ ] **Video < 3 minutes** with a per-second script, recorded in a single session.
- [ ] **Deck PDF 10 slides, English.** All submission materials in English.
- [ ] **Every number has a source** in §9 or a named study. No invented numbers.
