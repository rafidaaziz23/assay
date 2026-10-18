# AUDIT.md — Critical Assessment & Winning Strategy (v2.0.0)
## Assay: The Active Socratic Learning Engine

**Auditor:** AI Strategic Advisor (Brutally Honest Mode)
**Date:** October 14, 2026 — second revision of the October 13 audit
**Deadline:** October 18, 2026, 23:59 UTC+8 — **HARD DEADLINE** (4 working days left)
**Contracts audited:** `PRD.md` v2.0.0 + `API-CONTRACTS.md` v2.0.0 (status: OPERATIONAL CONTRACT, frozen Oct 14)
**Status:** PRE-BUILD AUDIT — contracts are frozen, **no product code yet**.

### Changelog for this audit (v1 → v2)

| Area | v1 (Oct 13) | v2 (Oct 14) |
|---|---|---|
| Product name | CogniForge | **Assay** |
| Deadline | "Oct 18, not 19" (finding) | Oct 18 confirmed in PRD v2 §header — **RESOLVED** |
| Track | "Track 4 AND 5, pick one" | Track 4 only in PRD v2 — **RESOLVED** |
| Scope | "18 sub-features, 5-week scope" | PRD v2 §8 cut list exists — **PARTIAL**, see §1 |
| Anti-cheat | "security theater, don't sell it" | ADR 003: on-device ML + auto-blur + Accessible Mode — **RESOLVED** |
| Honeypot | "not yet validated, assumption" | Now empirically tested (n=80, 4 models) — **PARTIAL**, see §12 |
| Fallback | "none, must exist" | `DEMO_MODE=cached` + auto-trigger 429/500/503 — **RESOLVED** |
| Numbers | — | Every number in this document is traceable to `../reza-research/parts10/HASIL-TES-EMPIRIS.md`. No invented numbers. |

> Link note: all references in this document use paths relative to `active-learning-engine/`. The `file:///D:/Lab/nexatriv/...` links in audit v1 are dead and have been removed.

---

## ⚠️ PREAMBLE: REALITY CHECK

Today is **October 14**. The deadline is **October 18, 2026, 23:59 UTC+8** (organizer timeline: `../01-event-guidelines/02-timeline-schedule.md` — `>>> SUBMISSION DEADLINE: OCTOBER 18, 2026 <<<`). **4 calendar days** remain, and the PRD itself targets submitting on Day 4 before 20:00.

Four mandatory deliverables:
1. Live Prototype (Cloud Run / Firebase)
2. Demo Video ≤ 3 minutes
3. Pitch Deck PDF (10-12 slides)
4. A tidy public GitHub repository

What already exists: PRD v2, API-CONTRACTS v2 (LOCKED), ADR 001-005, DEMO-SCRIPT, PITCH-DECK-OUTLINE, COMPETITIVE-ANALYSIS, empirical numbers. **What does not exist: code, a working eval harness, deploy, video, final deck.** That is the first fact to face, and it is unchanged from audit v1.

---

## 1. STATUS OF AUDIT v1 FINDINGS — RESOLVED / PARTIAL / OPEN

This is the core of this revision: every old finding gets a status and evidence, rather than being left hanging.

| # | Old finding | Status | Evidence / notes |
|---|---|---|---|
| 1.1 | PRD states deadline Oct 19 (wrong) | ✅ **RESOLVED** | PRD v2 header: `October 18, 2026, 23:59 UTC+8 — HARD DEADLINE`. The §6 v2 schedule also ends Oct 18. |
| 1.2 | Scope inflation: 5 pillars / ~18 sub-features / 5-week scope | ⚠️ **PARTIAL** | PRD v2 §8 has an explicit cut list (Monaco+Piston+TDL, visual DAG, dual-metric, voice/Gemini Live, auth, multi-source). But §5 v2 itself computes **~14.75 dev-days vs ~9.6 dev-days of capacity**. The cut resolves the *definition* of scope, not the *arithmetic*. See N1 in §9. |
| 1.3 | Track 4 AND Track 5 alignment (ambiguous, 1 team = 1 track) | ✅ **RESOLVED** | PRD v2: `Track Alignment: Track 4 … single track`. COMPETITIVE-ANALYSIS v2 line 7 matches. |
| 1.4 | PRD is inward-looking: target user vague, no numbers, JAPAC untouched | ⚠️ **PARTIAL** | PRD v2 §2.3 adds personas (B2C demo: student/dev by role; B2B story: bootcamp & corporate L&D) + JAPAC (9 million digital talent gap, World Bank; bootcamp completion <15%). **Still OPEN:** no TAM/SAM/SOM, no defensible retention/ROI claim. `../market-sizing-guide/` exists in the repo but the PRD does not use it. |
| W1 | Scope too large for the build time | ⚠️ **PARTIAL** | Same as 1.2. See N1. |
| W2 | Browser-side anti-cheat = security theater | ✅ **RESOLVED** | ADR 003 explicitly rejects CSS-only anti-cheat; replaced by on-device Focus Mode + "integrity signal" framing. PRD §7 no longer uses the word "anti-cheat" as a claim. |
| W3 | Honeypot not empirically validated — assumption | ⚠️ **PARTIAL (up from OPEN)** | Now measured: **54% hallucination (n=80, 4 models)**; per model gemini-flash-medium **75%**, deepseek-v4-pro 70%, deepseek-v4-flash 45%, deepseek-v4.1-flash 25%. The claim "external LLMs will hallucinate" is **proven in direction, not 100%**. 29/80 calls REFUSE, 5 HEDGE, 3 ERROR. Real residual risk → model pinning in the demo is mandatory (§7.2, N4). |
| W4 | LLM judging LLM = subjective, no deterministic guardrail | ⚠️ **PARTIAL** | ADR 002 (deterministic classification from structured output) + verifier loop (**13/20 hallucinations caught, 65%**) + appeal path + `confidence` field. But the verifier **misses 35%** — never claim "verified", claim "second-pass check". |
| W5 | No fallback mode | ✅ **RESOLVED** | API-CONTRACTS §3: trigger on `DEMO_MODE=cached` OR header `x-demo-mode: cached` OR Gemini error 429/500/503; 2 required scenarios (success flow + caught flow). |
| W6 | Submission language must be English, PRD is in Indonesian | ⚠️ **PARTIAL** | PRD v2 §7 states UI/README/deck/video = English, internal documents = Indonesian. The rule is settled; **not a single English artifact exists yet**. This copywriting effort is not yet in the Day 4 budget. See N11. |
| 5.1 | No ADRs / formal architecture | ⚠️ **PARTIAL** | ADRs 001-005 now exist in `docs/adrs/` (model selection, deterministic guardrails, client-side ML, role taxonomy, honeypot catalog). **Still OPEN:** no architecture diagram (C4/container) in the repo — the "System Architecture Accuracy" rubric line will look for this. |
| 9.3 | Monaco + Piston + TDL = a project of its own | ✅ **RESOLVED** | PRD v2 §8: cut to roadmap. API-CONTRACTS v2 §0 removes the `DEBUG_CHALLENGE` state. |
| 9.4 | Browser-side anti-cheat sold as security | ✅ **RESOLVED** | ADR 003 + PRD §4.5. |
| 9.5 | 4 devs with no API contract | ✅ **RESOLVED** | `API-CONTRACTS.md` v2 LOCKED (Oct 14), 8 endpoint groups + state machine + JSON schema. Team is now 3 devs (PRD §5). |
| 9.6 | Timeline starts Oct 14 but the document was written the night of Oct 13 | ✅ **RESOLVED** | Day 0 = Oct 14 spent on contracts + honeypot numbers — and it **was actually finished today**. |
| 9.7 | Honeypot `trigger_round: 2` hardcoded → never fires if the interview is only 1 round | ❌ **STILL OPEN** | API-CONTRACTS v2 §2.5 example still places the honeypot at `turn_index: 2`. If the user (or the demo) calls `finalize` after 1 round, the honeypot is never injected. Fix: force a minimum of 2 rounds before `finalize`, or inject in round 1 when the interview is expected to be short. |
| 9.8 | No Q&A defense script | ✅ **RESOLVED** | §10 of this document, already updated for v2. |

**Honest score: 8 RESOLVED, 8 PARTIAL, 1 OPEN.** The team is moving fast and the direction of the fixes is right. But the remaining "PARTIAL" items all pile up in the same place: **4-day capacity**.

---

## 2. SWOT ANALYSIS (HONEST) — updated

### 2.1 STRENGTHS

| # | Strength | Justification |
|---|----------|-------------|
| S1 | **The "Anti-AI-Brain-Rot" narrative is still zeitgeist** | 95% of university students use AI (HEPI 2026); 67% of students say AI damages their thinking (RAND, Mar 2026); PISA 2025 is the lowest in history. Google Cloud judges are aware that their own product (NotebookLM) is seen as part of the problem. Raising this = courage + awareness. |
| S2 | **The honeypot now has numbers, not opinions** | 54% hallucination (n=80, 4 models). No learning platform injects fictional concepts to detect thought outsourcing. Novel, demo-friendly, and **measurable**. |
| S3 | **AI as "Enforcer", not "Assistant"** | 99% of hackathon projects build an AI helper. Reversing the role into an adversarial tutor separates Assay from hundreds of competitors. |
| S4 | **Strong alignment with Track 4** | Track 4 = Media, Content & Digital Experiences, sub-theme adaptive learning for retention. It is practically written for Assay. |
| S5 | **Contracts & ADRs already frozen on Day 0** | This is what usually kills hackathon teams on Day 2. Already done. |

### 2.2 WEAKNESSES

| # | Weakness | Impact & Reality |
|---|----------|-------------------|
| W1 | **Capacity arithmetic still shows a ~5 dev-day deficit** | PRD v2 §5: 14.75 dev-days vs ~9.6 effective. The §8 cut list drops roadmap items, not items already counted in that 14.75. This is risk #1 and it is still live. |
| W2 | ~~Browser-side anti-cheat = theater~~ | **Closed.** ADR 003. But never slide back into the "anti-cheat" claim — that is the entry point for one fatal judge question. |
| W3 | **Honeypot at 54%, not 100%** | That number is strong for the deck and honest for Q&A, but **not a demo guarantee**. 29 of 80 calls actually REFUSE. The demo must use a `fictional_term` (100% effective at n=12 valid, highest of the 4 traps) on the model that is easiest to bait. |
| W4 | **Reasoning assessment is still LLM-mediated** | Deterministic classification (ADR 002) reduces subjectivity and the verifier catches 65%. The rest remains a judgment call — admit it in the deck, do not hide it. |
| W5 | ~~No fallback~~ | **Closed.** API-CONTRACTS §3. |
| W6 | **All submission artifacts are still Indonesian / do not exist yet** | UI, README, deck, video must be English (`../01-event-guidelines/04-rules-eligibility.md` §2). See N11 — the AI response examples in API-CONTRACTS are still in Indonesian. |
| W7 | **No code.** | Four days for 12 must-ship items (§6). There is no path to adding new features after this document. |

### 2.3 OPPORTUNITIES

| # | Opportunity | How to exploit it |
|---|-------------|---------------------|
| O1 | **No competitor takes an "anti-AI" position at an AI competition** | A memorable paradox. Deck slide 1: *"Every AI study tool answers questions. Assay questions your answers."* |
| O2 | **Judges like deterministic guardrails** | The honeypot is a deterministic trap with structured classification; the result is auditable (`honeypot_verdict` + `evidence_quotes` in the report), not "the AI said so". |
| O3 | **On-device ML as proof of the Google stack beyond Gemini** | MediaPipe is a Google product, zero tokens, zero inference cost, and visually very convincing in a demo. Already decided (ADR 003), no longer a proposal. |
| O4 | **B2B / competence verification angle** | Bootcamps with completion <15% and untrustworthy certificates = pain someone will pay for. Venture/enterprise judges will ask this (§10 Q10). |
| O5 | **Your own empirical numbers as Technical Merit evidence** | It is very rare for a hackathon team to have its own test results with n, model list, and raw logs. Use this on the "Evidence" slide — a 3-row table, not 10 slides. |

### 2.4 THREATS

| # | Threat | Severity | Mitigation |
|---|--------|----------|------------|
| T1 | User uses a second device (phone) to browse answers | 🔴 CRITICAL | Browser-side is useless here. The only layer that truly works: the honeypot (§7.1 Layer 4). |
| T2 | Latest LLMs refuse to answer fictional concepts | 🟠 HIGH | **Already measured**: 25%-75% per model. Pin the model, rotate terms from the catalog (ADR 005), prepare a cached scenario. |
| T3 | Judges see "focus mode" as too restrictive / not accessible | 🟠 HIGH | Accessible Mode + integrity-signal framing + score marked `assisted_unverified` (§4). |
| T4 | Another competitor also builds an adaptive learning platform | 🟡 MEDIUM | Moat = honeypot + calibration gap + adversarial positioning. "Adaptive quiz" alone is not enough. |
| T5 | Gemini rate limit / down during the demo | 🟠 HIGH | `DEMO_MODE=cached` with 2 scenarios (success + copy-paste-caught). Non-negotiable. |
| T6 | **Focus Mode eats Day 3 and the demo ends up half-finished** | 🟠 HIGH | New in v2 (MediaPipe promoted to must-ship). Mitigation: camera optional, cached scenarios need no camera, blur = a 30-line JS overlay. See N2. |
| T7 | **Scope stops at the document, not in the code** | 🔴 CRITICAL | The only mitigation: no new features on Day 4. Period. |

---

## 3. COMPETITOR DEEP-DIVE

### 3.1 Direct Competitors (existing active learning platforms)

| Platform | What they already do | Assay's edge |
|----------|-------------------------------|------------------|
| **Khan Academy Khanmigo** | Socratic-method AI tutor, 2+ years in operation, funded by the Bill & Melinda Gates Foundation | **The toughest competitor.** But: no gatekeeping, no integrity detection, no self-service PDF upload, no enforcement. |
| **Google Learn About** | Google's interactive AI tutor, Socratic approach | No enforcement, no gatekeeping. Users can just ask for the answer — and they will get it. |
| **Quizlet AI** | Automatic flashcards + practice tests | Surface-level recall. No reasoning interrogation, no trace of reasoning. |
| **Coursera / Udemy AI** | Adaptive quiz after video | Passive. Users can watch while scrolling their phone. No friction. |
| **Duolingo** | Gamification + spaced repetition | Language only. Its gamification model (streak/XP) can be borrowed for engagement, not positioning. |
| **NotebookLM** | Summarize doc, generate podcast | This is "the villain" in Assay's narrative: the brain-rot enabler. Name it in the deck — it is bold, and the judges know it is their product. |
| **Foreman** (AI Builder Cup 2026 participant, Track 5) | "Honesty Canary": tests the honesty of **AI agents** with questions whose answers deliberately do not exist | Same mechanism DNA as Assay's honeypot. The difference is one sentence: Foreman tests the honesty of **agents**; Assay tests the honesty of **humans cheating with other agents**. Say it explicitly — judges will recognize the pattern and score Assay as the human-side mirror. |
| **Chopdesk** (Track 1) | Heuristic offline fallback when Gemini returns 429 | Not an opponent (different track), but a benchmark: Assay must have the same class of fallback. It already does (API-CONTRACTS §3). |

### 3.2 Khanmigo Risk Assessment

Judges **will** ask: *"How is this different from Khanmigo?"*

**Critical differentiation (use this order):**
1. Khanmigo is **suggestive**, not **enforcement**. Users can skip a Socratic session at any time; Assay locks the chapter until the score ≥ 75.
2. Khanmigo **does not detect integrity**. No honeypot, no focus signal.
3. Khanmigo **does not accept user documents**. You cannot "test me on my own course module".
4. Khanmigo **has no calibration gap** — the distance between "feeling you understand" and "actually understanding" never surfaces.

**What must be admitted in front of judges:** Khanmigo has been running 2+ years with effectiveness research, funded by a major institution. Assay is 4 days old. Do not claim total superiority — claim this: *"We build on a proven Socratic method and add the enforcement and integrity layer that nobody ships."* Admitting limits actually raises credibility.

---

## 4. THE MOBILE-CHEATING PROBLEM & ML CAMERA — **DECIDED**

### 4.1 Problem Statement

Browser-side anti-cheat (`onblur`, `oncopy`, `user-select: none`) is useless when:
- The user opens ChatGPT on a phone while studying on a laptop
- The user uses a second monitor / virtual desktop
- The user retypes the question manually
- The user uses a screen reader or accessibility tools

### 4.2 Final decision (ADR 003 — Accepted, no longer a recommendation)

```
+------------------------------------------------------------------+
|               FOCUS MODE — ON-DEVICE, NO VIDEO OUT               |
|                                                                  |
|  MediaPipe in-browser (client-side inference)                    |
|  --------------------------------------------------------------  |
|  Signals detected:                                               |
|   - GAZE_DRIFT       head-pose/gaze deviates > threshold         |
|   - MULTIPLE_FACES   face count > 1                              |
|   - TAB_BLUR         tab switch / window loses focus             |
|   - CAMERA_OFF       camera off / not permitted                  |
|                                                                  |
|  Sent to the server: ONLY boolean events + timestamp +           |
|  duration. `video_transmitted: false` is a REQUIRED field.       |
|  Video/images/embeddings NEVER leave the device.                 |
|                                                                  |
|  When a signal fires -> page AUTO-BLURS + `assisted` flag.       |
|  Blur = prevention + marker, NOT punishment: score still counts. |
+------------------------------------------------------------------+
```

**Consequences you must state yourself before the judges say them:**
1. **Accessible Mode** turns the camera off entirely (copying allowed, blur off, relaxed timing). The score is still computed and marked **`assisted_unverified`** — so an unverified session is never silently read as "clean".
2. **Detection is device-bound.** MediaPipe accuracy drops on cheap hardware, in poor light, with odd camera positions. The signal is **advisory, not authoritative**.
3. **False positives are contained.** Glancing down to write notes ≠ cheating. That is why the flag lowers the integrity score + goes into the report + can be appealed, rather than auto-failing.
4. **Not an anti-cheat claim.** No system is cheat-proof. What Assay sells: cheating costs more than learning.

### 4.3 Why this wins on the rubric (not just a feature)

| Reason | Rubric it hits |
|---|---|
| MediaPipe = Google stack beyond Gemini | Technical Merit (40%) |
| Zero LLM tokens, zero inference cost per frame | Technical Merit / Scalability |
| Live face tracking catching a user glancing at a phone = the most memorable visual demo | Innovation (25%) |
| On-device + `video_transmitted: false` = a privacy claim backed by the contract, not a promise | UX & Solution Design (10%) + Q&A Q4 |
| Accessible Mode + `assisted_unverified` = users with disabilities are not sacrificed | UX & Solution Design (10%) |

### 4.4 Token savings with client-side ML & telemetry

| Task | Without ML | With client-side ML/telemetry | Savings |
|------|----------|--------------------------------|-------|
| Detecting whether the user reads vs skips | Gemini evaluates read time vs text length (1 call/chapter) | Scroll + dwell telemetry in the frontend | ~500 tokens/chapter |
| Copy-paste detection | Gemini compares writing style (1 call) | `paste_detected` + `keystroke_cpm` that are **already in the contract** (API-CONTRACTS §2.5) | ~800 tokens/eval |
| Second-device cheating | Impossible without a camera | MediaPipe gaze/head-pose | N/A (impossible without ML) |
| Pre-filter before deep eval | Every answer is sent to Gemini | Rule-based filter (length, keywords, duration) → only suspicious ones go to deep eval | ~60% |

---
---

## 5. JUDGING CRITERIA OPTIMIZATION

Official rubric (`../01-event-guidelines/05-judging-criteria.md`): Technical Merit & Gen AI 40% · Problem Alignment & Impact 25% · Innovation & Creativity 25% · UX & Solution Design 10%.

### 5.1 Technical Merit & Gen AI Implementation (40%) — THE KING MAKER

| Sub-criterion | What judges look for | What must be shown | Current gap |
|---|---|---|---|
| Meaningful Use of Gen AI | AI = core engine, not a gimmick | Socratic interrogator + honeypot classifier + syllabus synthesis = AI drives the entire product | ✅ Strong |
| System Architecture Accuracy | Modular, deterministic, secure | ADRs 001-005 **already exist**; per-chapter state machine; locked JSON schema | ⚠️ ADRs done, **no architecture diagram yet** |
| Scalability & Resilience | Error handling, fallback, latency | `DEMO_MODE=cached` + auto-trigger 429/500/503 (API-CONTRACTS §3) | ✅ Closed in v2 |
| Advanced AI Techniques | Not a prompt wrapper | Structured output (4/4 valid JSON), Flash/Pro model routing, verifier loop, MediaPipe, PDF-RAG | ✅ Strong **if executed** |
| Eval harness + numbers | Benchmarks folder, not claims | Numbers already exist (n=80, n=48, 13/20, 4/4) — they just need wrapping into a re-runnable `benchmarks/` + `eval/` | ⚠️ Numbers exist, harness does not |

**Action items for the 40%:**
1. A re-runnable `benchmarks/` + `eval/`, with a short README and stored output. Numbers without a harness = claims.
2. A container architecture diagram (frontend / API / Gemini / Firestore / MediaPipe on-device) — one PNG, not three.
3. An ADR 001-005 table in the README with one line each on "what was rejected and why".

### 5.2 Problem Alignment & Impact (25%)

| Sub-criterion | Gap | Fix |
|---|---|---|
| Track 4 specific friction | ✅ Strong — brain rot / passive consumption | Use the organizers' problem statement language on slide 2. |
| Quantifiable impact | ⚠️ Problem numbers exist (95%, 67%, PISA, 9 million gap); **product numbers do not** (no provable retention claim yet) | Do not invent retention claims. Use what is defensible: *calibration* (calibration gap) and *integrity* (54% honeypot) as metrics Assay actually measures. |
| JAPAC relevance | ✅ Closed in v2 §2.3 (World Bank 9 million digital talent; bootcamp completion <15%) | Add one line on "why Indonesia/SEA first" in the deck. |
| Specific target user | ⚠️ Still two directions (B2C demo + B2B story) | For the deck: **B2C demo, B2B money**. One sentence, not two pitches. |

### 5.3 Innovation & Creativity (25%)

| Sub-criterion | Status | Action |
|---|---|---|
| Differentiation & originality | ✅ Pedagogical honeypot + AI-as-enforcer + calibration gap. Three things that do not exist in current products. | Cite Foreman as the philosophical mirror (§3.1). |
| Beyond superficial | ✅ Structured output + deterministic classification + hybrid RAG + on-device multimodal | Show the PDF-RAG page-anchor as part of the honeypot mechanism, not as an extra feature. |
| Multimodal | ✅ MediaPipe (decided) | The demo must show the events live, not just a slide. |

### 5.4 User Experience & Solution Design (10%)

**The tension must be framed, not hidden:** Assay is deliberately full of friction (gates, blur, timers), while judges reward ease of use.

> *"Friction is the feature, not the bug. We gate chapters the way a gym gates results — the resistance is the point."*

Two things that defuse the UX critique:
1. **Accessible Mode** that actually works (camera off, copying allowed, relaxed timing) — not a cosmetic toggle.
2. **The calibration slider** — one 10-second moment that makes the user feel measured, not judged. It is also the cheapest feature with the largest impact.

Mandatory: a "Guided Tour" slide or 3-step onboarding so judges do not get lost when they try the live build.

---

## 6. FINAL SCOPE — MUST SHIP vs CUT (aligned with PRD v2)

### 6.1 🟢 MUST SHIP (non-negotiable, all in PRD v2 §3)

| # | Feature | Justification | Effort |
|---|-------|-------------|--------|
| 1 | **Intake screen** (intent + role selector + optional PDF) | Entry point. Without it there is no product. | Medium |
| 2 | **Realtime checklist generation** (+ user edit check/uncheck) | The first personalization moment; checked items = syllabus input. | Medium |
| 3 | **Syllabus synthesis** (chunk → structured chapters + reference enrichment, PDF-RAG page-anchor) | PDF-RAG is what makes honeypot claims verifiable ("this term is on no page"). | High |
| 4 | **Gated chapter reader** (linear chapters, `next` LOCKED until score ≥ 75) | Core differentiator. No summary button. | Low-Medium |
| 5 | **Select-word Socratic ask** (+ multi-word suggested questions, `gave_direct_answer: false`) | The new feature that proves the thesis: the AI asks back. | Medium |
| 6 | **Multi-turn interview quiz, 2-3 rounds** (inferential questions, adaptive follow-up) | The heart of the product. | Medium |
| 7 | **Honeypot injection + 4-value classification** (`CRITICAL_REJECTION +2` / `AI_HALLUCINATION_COPYPASTE −2` / `UNVERIFIED_HONEST 0` / `EVASIVE −1`) — **a score dimension, not a gate** | The demo "wow moment". Must run perfectly. | Medium |
| 8 | **Calibration** (prediction before reveal) + `calibration_gap` | Cheapest feature, largest impact, absent from competitors. | Low |
| 9 | **Single score per chapter + final report** (cross-chapter score, calibration gap trend, integrity log, honeypot verdict) | Proof that assessment actually happened. | Low |
| 10 | **DEMO_MODE=cached** (2 required scenarios: success flow + caught flow) | If the API dies during the demo = game over. | Low |
| 11 | **Focus Mode camera** (MediaPipe on-device, 4 boolean events, auto-blur, Accessible Mode) | Technical Merit + Innovation + visual demo. | Medium |
| 12 | **Eval harness + numbers + ADRs + architecture diagram** | This is what turns "claims" into "evidence" on the 40% rubric. | Medium |

**Note:** the verifier loop + appeal path are must-ship even though they are cheap (one endpoint + one UI). PRD §8 lists the verifier as mandatory; appeal already exists in contract §2.8 and PRD §4.6.

### 6.2 🟡 SHOULD HAVE (only if time remains — do not force it)

| # | Feature | Justification | Effort |
|---|-------|-------------|--------|
| 13 | **`paste_detected` + `keystroke_cpm` telemetry** | **Already in API-CONTRACTS §2.5.** Just needs to be sent from the frontend. The cheapest integrity signal available. | Low |
| 14 | **Response pressure timer** (a signal, not auto-fail) | PRD §4.5. Measures the user's thinking time, not the model's wait time. | Low |
| 15 | **Google Search grounding for 1-2 chapters** (results cached) | Adds credibility to "reference enrichment". | Medium |
| 16 | **No-PDF path** (`source: role_taxonomy_generated`) | Saves the demo if the PDF fails to parse. Do not use it as the main demo flow. | Medium |
| 17 | **SSE streaming checklist** | If polling is enough for the demo, polling is cheaper and risk-free. | Medium |

### 6.3 🔴 CUT (roadmap slide only — do not touch on Day 4)

| # | Feature | Reason |
|---|-------|--------|
| 18 | Monaco + Piston + TDL (coding arena) | Does not fit in 4 days; not the wedge. |
| 19 | Visual DAG Skill Tree (ReactFlow) | Not a differentiator; the linear chapter stepper is free and clearer. |
| 20 | Dual-metric (2 separate scores) | Replaced by single score + calibration gap (cheaper, stronger). |
| 21 | Voice / Gemini Live | Latency + cost are risky live. |
| 22 | Complex auth / multi-user | 1 demo session is enough. |
| 23 | Multi-source input (video/audio) | PDF is enough. |
| 24 | Excalidraw / diagram evaluation | Scope creep. |
| 25 | Full keystroke dynamics engine | `paste_detected` alone is enough (#13). |

### 6.4 Feature → Rubric

```
JUDGING RUBRIC (100%)
|
+-- Technical Merit 40% ....... Socratic interview + verifier, structured output,
|                              MediaPipe, eval/ + benchmarks, cached fallback
+-- Problem & Impact 25% ...... problem numbers (HEPI/RAND/PISA), JAPAC 9M gap,
|                              one B2B story (not two pitches)
+-- Innovation 25% ............ honeypot + 54% evidence, calibration gap,
|                              select-word Socratic, AI-as-enforcer
+-- UX & Solution Design 10% .. Accessible Mode + assisted_unverified, calibration
                               slider, guided tour, SSE streaming
```

---
## 7. THREAT MITIGATION PLAYBOOK

### 7.1 Threat: user cheats with a second device

| Layer | Tactic | Effectiveness |
|-------|--------|-------------|
| **Layer 1 — Paste/telemetry** (client) | `paste_detected` + `keystroke_cpm` + duration (already in the contract). A long answer appearing in <2 seconds = flag. | 🟢 High for paste detection |
| **Layer 2 — Response time analysis** (backend) | An inferential question answered in <15 seconds with a long paragraph = suspicious. | 🟡 Medium — false positives for fast typists |
| **Layer 3 — MediaPipe focus signals** (client ML) | `GAZE_DRIFT` / `MULTIPLE_FACES` / `TAB_BLUR` → auto-blur + `assisted` flag. | 🟡 Medium — many false positives, advisory |
| **Layer 4 — Honeypot** (AI-level) | The only defense that truly works against an external LLM, whatever the device. **54% hallucination measured; `fictional_term` 100% effective (n=12 valid).** | 🟢 High (not 100% across the population) |
| **Layer 5 — Consistency cross-check** (AI-level) | The next round asks about the same concept with different framing. Contradictory answers = "inconsistent understanding". | 🟢 High |
| **Layer 6 — PDF-RAG anchor** (AI-level) | The user's claim is verified against document pages. A term/quote that appears on no page = signal. | 🟢 High (if the demo uses a PDF) |

**Verdict:** never rely on a single layer. And be honest with judges: **no system is cheat-proof** — what Assay does is make cheating cost more than learning. The line used in the deck and Q&A: *"We don't prevent cheating. We make it more effort than learning."*

### 7.2 Threat: honeypot fails (modern LLMs refuse to hallucinate)

**Status: measured, no longer an assumption.** n=80 calls, 4 models:

| Model | Hallucination | Refuse | Hedge | Error | Avg latency |
|---|---|---|---|---|---|
| ag/gemini-3.8-flash-medium | **75%** | 3 | 2 | 0 | 13s |
| z/deepseek-v4-pro | 70% | 4 | 2 | 0 | 30s |
| z/deepseek-v4-flash | 45% | 10 | 0 | 1 | 22s |
| z/deepseek-v4.1-flash | **25%** | 12 | 1 | 2 | 34s |
| **TOTAL** | **54%** | 29 | 5 | 3 | 25s |

Effectiveness by trap type (n=48): `fictional_term` **100%** (10 comply / 0 pushback / 2 error, n=12 valid) · `trap_number` 58% · `false_premise` 25% · `over_claim` 25%.

**Mitigations that must be executed:**
1. **Pin the model in the demo.** Never demo on deepseek-v4.1-flash (25%). The models that are easiest to bait are already identified.
2. **Use `fictional_term`, not `false_premise`/`over_claim`.** 25% is too weak for a moment that must run perfectly.
3. **Rotate terms from the catalog (ADR 005).** Provide 20-30 terms per domain so the demo does not depend on a single term.
4. **Never write "100%" or "always proven" in the deck.** Write 54% (n=80) — an honest number is stronger than a superlative, and technical judges will respect the n.
5. **A cached scenario as a safety net.** If the live LLM refuses, the caught flow still exists in `DEMO_MODE=cached`.

### 7.3 Threat: judges feel the UX is too restrictive

1. Show **Accessible Mode** explicitly in the UI (camera off, copying allowed, relaxed timing) and explain the consequence: the score is marked `assisted_unverified`.
2. Frame the friction as a **pedagogical design pattern**: *"Desirable Difficulties"* (Bjork) — deliberate difficulty improves long-term retention.
3. Open with the disclaimer: *"This product is intentionally hard. That's the point."*
4. Never use the word "anti-cheat" as a security claim. Say **focus & integrity signal**.

### 7.4 Threat: Gemini down / rate limited during the demo

1. Trigger: `DEMO_MODE=cached` OR the header `x-demo-mode: cached` OR error 429/500/503 (API-CONTRACTS §3).
2. **Two required scenarios:**
   - **Success flow** — a critical user rejects the honeypot → `CRITICAL_REJECTION`, high score, chapter unlock.
   - **Caught flow** — the user copy-pastes an external LLM answer → `AI_HALLUCINATION_COPYPASTE`, score drops, integrity flag.
3. The `LOCAL_DETERMINISTIC_CACHE` banner **may appear on camera** — it is a resilience feature, not a glitch. The line: *"Gemini mocked for resilience."*
4. The cache also stores external grounding results so the demo does not depend on the network.

---

## 8. FEATURE PRIORITY & INTERNAL WEIGHTING

### 8.1 Contribution of each feature to the judge rubric

| Feature | Tech Merit (40%) | Problem Impact (25%) | Innovation (25%) | UX (10%) | Total | Priority |
|-------|:---:|:---:|:---:|:---:|:---:|:---:|
| Socratic interview multi-turn + verifier | ★★★★★ | ★★★ | ★★★ | ★★ | **30%** | P0 |
| Honeypot trap + deterministic classification | ★★★★ | ★★ | ★★★★★ | ★ | **25%** | P0 |
| Syllabus + PDF-RAG + gated reader | ★★★★ | ★★★★ | ★★★ | ★★★ | **18%** | P0 |
| Focus Mode MediaPipe (on-device) | ★★★★ | ★★ | ★★★★ | ★★ | **10%** | P0 |
| Eval harness + benchmarks + ADRs/diagram | ★★★★★ | ★ | ★ | ★ | **8%** | P0 |
| Cached fallback mode | ★★★★★ | ★ | ★ | ★★★★ | **5%** | P0 |
| Calibration + report | ★★ | ★★★ | ★★★★ | ★★★★ | **4%** | P0 |
| Paste/telemetry + response timer | ★★★ | ★ | ★★ | ★★ | **—** | P1 |

### 8.2 Effort vs Impact (read as a schedule)

Every P0 in the **left** quadrant (Socratic+verifier, honeypot, syllabus+PDF-RAG+gate, cached fallback, calibration+report) must be finished before Day 4. Focus Mode and the eval harness sit in the low-effort/high-impact corner — both have safety nets (camera optional; numbers already exist), so either may drop to a minimal form if Day 3 runs out. Monaco/Piston and the visual DAG sit in the high-effort corner: **cut**, do not build them in any form.

---

## 9. WHAT THE PRD GETS WRONG (v2 — updated)

Lines **already fixed in v2** are still listed so that nobody revives the problem.

| Section | Problem | Status | Fix |
|---|---|---|---|
| §1.2 v1 — buzzword "High-Friction, High-Reward" with no operational definition | A slogan, not a specification | ⚠️ **PARTIAL** | PRD v2 §3 defines it through flow (locked chapters, no summary button, score gate ≥75), but the phrase still appears in §1.2 without a single operational sentence. Add an explicit definition in the deck notes. |
| §3.3 v1 — Monaco + Piston + TDL | A project of its own | ✅ **RESOLVED** | Cut to roadmap (PRD v2 §8); the `DEBUG_CHALLENGE` state is removed from the contract. |
| §3.4 v1 — browser-side anti-cheat sold as security | Security theater | ✅ **RESOLVED** | ADR 003 explicitly rejects it; replaced by Focus Mode + integrity-signal framing. |
| §4 v1 — 4 developers without an API contract | Integration impossible | ✅ **RESOLVED** | `API-CONTRACTS.md` v2 LOCKED; the team is now 3 devs with per-pillar ownership. |
| §5 v1 — timeline starts Oct 14, document written the night of Oct 13 | Day 1 lost to planning | ✅ **RESOLVED** | Day 0 (Oct 14) spent on contracts + numbers; **finished today**. |
| §6 v1 — honeypot `trigger_round: 2` hardcoded | The honeypot never fires if the interview is 1 round | ❌ **OPEN** | API-CONTRACTS §2.5 still places the honeypot at `turn_index: 2`. Force a minimum of 2 rounds before `finalize`, or inject in round 1 for short interviews. **Test this path before recording the video.** |
| §7 v1 — winning playbook without Q&A defense | Judges will challenge, the team will stumble | ✅ **RESOLVED** | §10 of this document. |

### NEW findings in v2 (not present in audit v1)

| # | Finding | Severity | Fix |
|---|---|---|---|
| N1 | **The §5 arithmetic does not close.** PRD v2 itself writes ~14.75 dev-days vs ~9.6 capacity. The §8 cut list contains roadmap items (Monaco/DAG/voice), not items already counted in the 14.75. | 🔴 CRITICAL | Pick one: (a) cut another 5 dev-days from the flow (candidates: SSE → polling, no-PDF path, appeal UI, Google Search grounding), or (b) drop the demo target to 2 chapters instead of 3, or (c) accept 12 working hours/day and write that into the schedule. What is not allowed: pretending the deficit is not there. |
| N2 | **Focus Mode was promoted to must-ship but scheduled for Day 3**, together with scoring + calibration + report + cached fallback. That is four heavy items in one day. | 🟠 HIGH | Build Focus Mode as a standalone component first (camera → event → blur), integrate it last. The cached scenarios need no camera at all. |
| N3 | **The four "research-mandatory features" (eval harness, verifier, calibration, cached fallback) = 3.5 dev-days** by the PRD's own count, and all of them land on Days 3-4, when the team is most tired. | 🟠 HIGH | Move the eval harness to Days 1-2 (it needs no UI, only finished endpoints). If it slips to Day 4, it will be lost. |
| N4 | **The honeypot is not a demo guarantee.** 54% aggregate; 25% on one model. | 🟠 HIGH | Pin the model (gemini-flash-medium 75%), use `fictional_term` (100% at n=12), rotate terms (ADR 005), prepare a cached caught-flow. |
| N5 | **The word "anti-cheat" still appears in PRD v2** (§3 Step 5 line "Anti-cheat feature", §5 diagram "anti-cheat"). ADR 003 already rejects that framing. | 🟡 MEDIUM | Replace with "Focus Mode / integrity signal" throughout. A small inconsistency, but judges do read the documents. |
| N6 | ~~**The UI must be English, but the AI response examples in API-CONTRACTS are still in Indonesian.**~~ **RESOLVED.** The contract examples were the outlier, not the runtime: `frontend/src/mocks/*.json` and `backend/app/core/fallback.py` already return English. §2.4 and §2.5 examples were rewritten to match the shipped fixtures. | ✅ FIXED | If the demo records an English UI with Indonesian AI replies, it looks unfinished. Done: contract now matches the runtime, so an English UI no longer implies a translation gap. |
| N7 | **No architecture diagram.** The ADRs are good, but the rubric says "System Architecture Accuracy". | 🟡 MEDIUM | One container diagram, in the README + slide 6. Half a day of work, large impact on the 40% rubric. |
| N8 | **`assisted` vs `assisted_unverified` are not used consistently.** PRD §4.5 uses the `assisted` flag for two different situations (cheating detection vs Accessible Mode). | 🟡 MEDIUM | Use the split from ADR 003: detection → `assisted`; camera off → `assisted_unverified`. Contract §2.7 is already correct; align the PRD and the UI. |
| N9 | **Number discipline — RESOLVED.** Deck v1 wrote "91.3% / 640ms" with no source (already removed). The `fictional_term` discrepancy (old logs 67%/90% vs canonical 100%) has been traced: the 67% figure was wrong because it counted ERROR as PUSHBACK. Canonical = 10 comply / 0 pushback / 2 error (n=12 valid). | 🟢 RESOLVED | All documents now use 100% (n=12) + state the n. Do not use 67%/90% again. |
| N10 | **Competitor positions can be misread.** FOREMAN and CHOPDESK are in different tracks — they are quality benchmarks, not head-to-head opponents. | 🟡 MEDIUM | In the deck, present them as "quality benchmarks" and take the lessons (honesty canary, fallback), not as opponents that were beaten. |
| N11 | **All submission artifacts (UI copy, README, deck, video) are still at zero.** English is mandatory. | 🟠 HIGH | Put English copywriting into the Day 4 budget explicitly, not as "leftover time". |
| N12 | **The default state of Focus Mode is undecided.** If the camera defaults to off, the most visual demo moment disappears; if it defaults to on, the accessibility critique arrives. | 🟡 MEDIUM | Default: camera **on** during the interview quiz, with a clearly visible Accessible Mode toggle on screen. Explain the score consequence in the UI when the toggle is pressed. |

---
## 10. JUDGE Q&A DEFENSE SCRIPT

The questions that will almost certainly be asked, with the answers to memorize.

### Q1: "How is this different from Khanmigo / Google Learn About?"
> **A:** "Khanmigo and Learn About are *suggestive tutors* — they ask Socratic questions, but accept any answer and move on. Assay is an *enforcement engine*: the next chapter stays locked until your reasoning passes evaluation, score ≥ 75. Beyond that, Assay injects fictional concepts to catch users who outsource their thinking to an external LLM — and we measured it: **54% hallucination across 80 calls to 4 frontier models**. We do not claim to beat Khanmigo; we build on a proven Socratic method and add the enforcement and integrity layer that nobody ships."

### Q2: "Browser-side anti-cheat is trivial to bypass. What actually prevents cheating?"
> **A:** "Correct, and that is why we do not use it. ADR 003 rejects `user-select: none` and forced blur as security theater. The layers that actually work sit at the AI level: (1) the honeypot — 54% measured, and our strongest trap type (fictional_term) baits a confident answer in 100% of valid calls (n=12); (2) cross-round consistency checks; (3) verification of claims against document pages via PDF-RAG. We call MediaPipe Focus Mode an *integrity signal*, not security — the signal is advisory. No system is cheat-proof; we make cheating cost more than learning."

### Q3: "What if the AI misjudges an answer that is actually correct?"
> **A:** "Three layers. One, assessment runs on a JSON schema with deterministic classification (ADR 002) — not a free-text judge, and every assessment carries `evidence_quotes` plus a `confidence` value. Two, there is a second-model verifier: in our tests it caught **13 of 20 hallucinations (65%)** — we are honest that 35% slip through. Three, there is an appeal path: the user can contest the score, and the system marks it `revised` or `uncertain`. Every trace of reasoning is stored for audit."

### Q4: "What about user privacy? You turn on the camera."
> **A:** "Video never leaves the device. MediaPipe inference runs in the browser; only boolean events reach the backend — `GAZE_DRIFT`, `MULTIPLE_FACES`, `TAB_BLUR`, `CAMERA_OFF` — with a timestamp and duration. The payload is required to carry `video_transmitted: false`, and that is written into our API contract, not just promised on a slide. We have no video pipeline, so there is no biometric retention, no video consent flow, and no high-risk AI Act classification for remote proctoring. Accessible Mode turns the camera off entirely; the score is still computed and marked `assisted_unverified` so the report stays honest."

### Q5: "This is too restrictive. Users will get frustrated and quit."
> **A:** "The friction is deliberate — we point to the 'Desirable Difficulties' research (Bjork): deliberate difficulty improves long-term retention. What matters is that our friction is bounded and transparent: one gate per chapter, a threshold of 75, and an Accessible Mode that turns off the camera, allows copying, and relaxes timing. We do not sell comfort; we sell proof of understanding. If a user wants instant summaries, NotebookLM already exists."

### Q6: "54% is not 100%. What if the LLM refuses to answer your fictional term?"
> **A:** "Correct, and that is why we measured before building. Across 80 calls to 4 models: 43 hallucinated, 29 refused, 5 hedged, 3 errored. We also know which model is easiest to bait — 75% on one model, 25% on another — so we pick the model and the trap type from data, not hope. We have a deterministic term catalog with variation (ADR 005) so it cannot be memorized, and a cached scenario if the live call fails. In the deck we write 54%, not 100%. A traceable number is more useful than a superlative."

### Q7: "Isn't this just proctoring / surveillance?"
> **A:** "No. Proctoring sends video to a server and builds a biometric pipeline; we reject that because the privacy cost is permanent and the detection gain is marginal at our scale. We monitor focus, not people: the signals are boolean, inference is on-device, and the consequence is a flag plus auto-blur — not a ban, not a report to an institution. And we never call this anti-cheat."

### Q8: "If no PDF is uploaded, does the product still work?"
> **A:** "It works. Chapters are generated from the role taxonomy plus grounding, and tagged `source: role_taxonomy_generated` so the origin is clear. But we are honest: the PDF path is the strongest, because PDF-RAG provides page-anchors — and those page-anchors are what make honeypot claims verifiable ('this term is on no page of your module')."

### Q9: "This is just studying. What's the business model?"
> **A:** "The demo is B2C, but institutions pay. Bootcamps with completion rates below 15% and certificates nobody trusts any more need proof of competence, not grades. Assay gives them a per-chapter reasoning score, a calibration gap trend, and an auditable integrity log. The JAPAC relevance is concrete: a 9 million digital talent gap (World Bank), and unverified graduates are a problem industry pays for."

### Q10: "Why MediaPipe and not Gemini Vision?"
> **A:** "Three reasons. One, privacy: no video is sent, so there is no biometric pipeline. Two, cost: zero tokens for focus detection, and detection runs every frame at no API cost. Three, latency: no network round-trip for a signal that must be instant. We acknowledge the trade-off: accuracy is bound to device quality and lighting, so the signal is advisory — which is why the flag affects the integrity score and can be appealed, rather than failing the session."

---

## 11. FINAL RECOMMENDATIONS

1. **CLOSE THE ARITHMETIC TODAY, NOT TOMORROW.** PRD v2 §5 itself shows a ~5 dev-day deficit (14.75 vs 9.6). Pick one path: cut more, drop the target to 2 chapters, or add working hours and write them into the schedule. Every new feature after this document = a feature that sacrifices the gate, scoring, or fallback.
2. **PIN THE MODEL AND THE HONEYPOT TERMS NOW.** `fictional_term` (100% at n=12), the most easily baited model (75%), rotation from the catalog (ADR 005). Never demo on the 25% model.
3. **FOCUS MODE: BUILD IT AS A STANDALONE COMPONENT.** Camera → event → auto-blur → flag, without waiting for full integration. The cached scenarios need no camera, so the demo has a double safety net.
4. **MOVE THE EVAL HARNESS TO DAYS 1-2.** The numbers already exist (54%, 100%, 65%, 4/4); the harness only needs to wrap them and re-run them. This is the 40% rubric and it is the thing most often lost on Day 4.
5. **CACHED FALLBACK FROM DAY 1.** Two scenarios (success + caught). This is life-or-death insurance for the demo.
6. **NEVER SAY "ANTI-CHEAT".** Say "Focus Mode / integrity signal". Also fix that wording in PRD §3/§5 (N5) so the document and the presentation stay consistent.
7. **ALIGN THE LANGUAGE BEFORE RECORDING THE VIDEO.** UI, AI replies, README, deck, video = English. The Indonesian response examples in API-CONTRACTS §2.4/§2.5 must be replaced, otherwise the demo will look mixed (N6).
8. **ADD ONE ARCHITECTURE DIAGRAM.** Half a day of work, immediately felt on the "System Architecture Accuracy" rubric line (N7).
9. **TEST THE 1-ROUND HONEYPOT PATH.** The v1 finding that is still OPEN: if the user calls `finalize` after one round, the honeypot is never injected. Force a minimum of 2 rounds.
10. **PREPARE THE Q&A.** If the team stumbles when asked "how is this different from Khanmigo?" or "54% is not 100%", technical superiority will not save it. Memorize §10, especially Q2, Q4, Q6.
11. **DAY 4 = FREEZE.** No new features, no big refactors. Only deploy, record, write the deck, and submit before 20:00 UTC+8.
12. **FINAL SELF-AUDIT, 1 HOUR.** Open PRD §3 flow and check one by one: can each step be shown live on camera? What cannot, move to the roadmap slide — do not force it.

---

## 12. EVIDENCE BASE (canonical numbers — do not invent)

Single source: `../reza-research/parts10/HASIL-TES-EMPIRIS.md` (local gateway, Oct 14, 2026 20:18, workers=5). Per-call raw logs are in `../reza-research/parts10/results/*.jsonl`.

| Metric | Number | n | Note |
|---|---|---|---|
| Honeypot hallucination rate (aggregate) | **54%** | 80 calls, 4 models | 29 REFUSE, 5 HEDGE, 3 ERROR |
| — ag/gemini-3.8-flash-medium | 75% | 20 | **Easiest model to bait — pin it for the demo** |
| — z/deepseek-v4-pro | 70% | 20 | Latency 30s |
| — z/deepseek-v4-flash | 45% | 20 | 1 error |
| — z/deepseek-v4.1-flash | 25% | 20 | **Do not use in the demo** |
| Trap effectiveness: fictional_term | **100%** (10 comply / 0 pushback / 2 error) | 12 valid | Strongest trap — use this one (small n, read it as "it works", not as a precise figure) |
| Trap effectiveness: trap_number | 58% | 48 | |
| Trap effectiveness: false_premise | 25% | 48 | Too weak for the demo |
| Trap effectiveness: over_claim | 25% | 48 | Too weak for the demo |
| Verifier loop catches hallucinations | **13/20 (65%)** | 20 | 4 passed, 3 unclear → real residual risk |
| Structured output valid JSON | **4/4 (100%)** | 4 | Strong claim, but small n — do not oversell it |

**Number rules:**
1. Every number in the deck, README, and video must be traceable to the table above or to a re-runnable `eval/`.
2. **Do not use superlatives** ("always", "100%", "proven"). Use the number + n.
3. Deck v1 once carried "91.3% / 640ms" with no source — PRD §9 already warns about this. Do not repeat it.
4. `fictional_term` = **100% (10 comply / 0 pushback / 2 error, n=12 valid)**. The 67% figure in the old logs is wrong: ERROR was counted as PUSHBACK. Do not use 67%/90%.
5. Classification uses transparent heuristic regex, not an LLM judge — that is deliberate so the measurement is not circular. Mention this if judges ask about methodology.
