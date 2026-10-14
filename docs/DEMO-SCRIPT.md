# Assay — 3-Minute Demo Video Script & Storyboard

**Product:** Assay: The Active Socratic Learning Engine
**Runtime:** 180 seconds (hard cap)
**Resolution / Frame Rate:** 1920x1080 (1080p) @ 30fps
**Language:** English (voiceover, UI, on-screen text)
**Audio:** Dry technical narration. No music bed over voiceover.
**Flow source of truth:** PRD v2.0.0 §3 (Kanonik) + API-CONTRACTS v2.0.0
**Evidence source:** `reza-research/parts10/HASIL-TES-EMPIRIS.md` — every number below is traceable to it.

---

## Storyboard & Timing Breakdown

| Timestamp | Screen Action & Visual | Spoken Voiceover | Key Objective |
| :---: | :--- | :--- | :--- |
| **00:00 - 00:20**<br>(20s) | **The problem.** Screen capture: a PDF of a module dropped into a generic AI chat, "Summarize" clicked, output scrolled past at speed. Cut to a scoreboard-style stat card. No logo, no team intro. | "95% of students now use AI. 67% of them say it is damaging their thinking. The tool answers instantly — and the reasoning muscle never gets trained. You finish the summary feeling fluent. Then an edge case shows up in a real interview, and it collapses." | Start on the problem. No title card, no introductions. |
| **00:20 - 00:50**<br>(30s) | **Intake screen (PRD §3 Step 1).** One screen, three inputs: free-text field "What do you want to learn today?" — type *"I want to understand how React rendering works internally"*. Role selector: Frontend / Backend / Fullstack / DevOps / Data-ML / Mobile / QA-Test / Security / System Design, plus **Others** (auto-surfaced when the intent does not match a seed role). PDF upload slot — **skipped** to prove it is optional, then re-run with the PDF attached. No "Summarize" button anywhere on screen. | "This is Assay. It does not summarize. You give it three things: what you want to learn, the role you are targeting, and — optionally — a document. No document works too. The chapter plan is generated from the role taxonomy instead. Assay never dispenses the answer; it interrogates the answer you give." | Establish the new entry point: intent-first, not upload-first. Show the absence of a summarize button. |
| **00:50 - 01:15**<br>(25s) | **Realtime checklist (PRD §3 Step 2).** Items stream in one by one (`checklist.partial` events) with a checkbox and an `origin` tag: `document`, `role_taxonomy`, `grounded_external`. User unchecks one item ("State batching semantics") and keeps the rest. | "The checklist streams in live from your intent, your role, and the document contents. Each item is tagged with where it came from. You edit the list before committing — unchecked items never become chapters. The plan is yours, not the model's." | Show realtime generation and user control over scope. |
| **01:15 - 01:40**<br>(25s) | **Syllabus synthesis (PRD §3 Step 3).** Three chapters appear with order, reading time, and `source_pages`. Open chapter 2's reference panel: a document anchor (page 7, `verified: true`) plus one `grounded_external` reference from Google Search grounding, marked `cached: true`. Chapter 2 shows status `LOCKED`. | "Assay chunks the document into structured chapters — title, order, objectives, reading time — and anchors every chapter to page numbers. Reference enrichment is grounded in your PDF first, which is mandatory; external search grounding is optional, limited to one or two chapters, and cached so the demo never depends on the network." | Prove PDF-RAG anchoring and cached grounding. |
| **01:40 - 02:05**<br>(25s) | **Gated chapter reader (PRD §3 Step 4).** Chapter 1 open, chapter 2 visibly `LOCKED`. User selects the word *"reconciliation"* → popover opens. AI replies with a counter-question, not a definition; the `gave_direct_answer: false` field is visible in the response panel. Then the user selects the multi-word phrase *"reconciliation and diffing"* → three suggested questions appear. | "Inside a chapter you can select any word and ask. Assay answers Socratically — it asks you back and points at the page. The flag on screen reads `gave_direct_answer: false`. Select a phrase instead, and it proposes the questions worth asking. Chapter two stays locked until you clear chapter one." | Demonstrate the select-word Socratic loop and the hard gate. |
| **02:05 - 02:45**<br>(40s) | **Interview quiz + honeypot + Focus Mode + calibration (PRD §3 Step 5).** Split screen.<br>Left: the interviewer asks an inferential question, then injects a honeypot — *"React Quantum Hook"* — with `honeypot_metadata.injected_term` visible.<br>Right: the same question pasted into an external LLM, which answers confidently and at length about a term that does not exist.<br>Left: user pastes that answer back → verdict `AI_HALLUCINATION_COPYPASTE`, honeypot score **-2**.<br>Re-run: user types *"React Quantum Hook is not in the React docs or any official library — you probably mean `useTransition` or `useDeferredValue`"* → verdict `CRITICAL_REJECTION`, honeypot score **+2**.<br>Focus Mode camera pane: gaze drift and a second face are detected on-device → page **auto-blurs**, event flagged `assisted`, `video_transmitted: false` on screen. Calibration slider: user predicts 90 before the reveal. | "Every chapter ends in an interview. Assay injects a fictional concept and reads the response. Across 80 calls on four models, they hallucinated a confident explanation 54% of the time — 75% on gemini-flash-medium, 70% on deepseek-v4-pro. Paste that back: `AI_HALLUCINATION_COPYPASTE`, minus two. Reject the premise: `CRITICAL_REJECTION`, plus two. Fictional terms drew a confident answer on every valid call; fake numbers, 58%. Focus Mode runs MediaPipe on-device — gaze drift, multiple faces, tab blur — and auto-blurs. No video leaves the device. The honeypot is a score dimension, not a gate. An integrity signal, not a claim that cheating is impossible." | The central mechanism. Show the trap working and show the honest-rejection path paying off. |
| **02:45 - 03:00**<br>(15s) | **Scoring, calibration gap, final report (PRD §3 Step 6).** Reveal: `chapter_score: 88`, threshold **>= 75** → chapter 2 unlocks. `calibration_gap: 2`, label `well_calibrated`. Then the report view: per-chapter scores, mean calibration gap, integrity flags, honeypot verdict log, and the appeal path. Close on the one-line positioning. | "One score per chapter, threshold 75 to unlock the next, and the gap between your predicted score and your earned one — your calibration gap. The report aggregates scores, calibration trend, integrity flags, honeypot verdicts, and a second-model appeal path. Thank you." | Land the measurement thesis and close. |

**Total: 180s.**

---

## Evidence Card (on-screen overlay, optional, use in the interview segment)

Every figure below comes from `reza-research/parts10/HASIL-TES-EMPIRIS.md`. Do not round up, do not add new ones.

| Claim | Figure | Sample |
| :--- | :--- | :--- |
| Honeypot hallucination rate (all models) | **54%** | n = 80 calls, 4 models |
| — gemini-flash-medium | 75% | 20 calls |
| — deepseek-v4-pro | 70% | 20 calls |
| — deepseek-v4-flash | 45% | 20 calls |
| — deepseek-v4.1-flash | 25% | 20 calls |
| Trap effectiveness: fictional_term | 100% (10 comply / 0 pushback / 2 error) | n = 12 valid |
| Trap effectiveness: trap_number | 58% | n = 48 |
| Trap effectiveness: false_premise | 25% | n = 48 |
| Trap effectiveness: over_claim | 25% | n = 48 |
| Verifier loop caught hallucinations | 13/20 (65%) | 20 hallucinated answers |
| Structured output valid JSON | 4/4 (100%) | 4 schema calls |

**Latency:** not quoted in the video. Numbers live in the `eval/` folder. Do not put a latency figure on screen unless it is read straight out of `eval/` on the day of recording.

**Banned:** the v1 script's sub-second latency percentile and its simulated-round-count figure have no source behind them. They must not appear in narration, overlay, or slide. Measured latency exists in `HASIL-TES-EMPIRIS.md` (average across models: 26s) but is not demo-relevant — leave latency out of the video entirely.

---

## Golden Rules for Recording

1. **No blank spinners, ever.** Every AI call in the take runs with `DEMO_MODE=cached` (or header `x-demo-mode: cached`). The cache holds both required scenarios: success flow (`CRITICAL_REJECTION`) and caught flow (`AI_HALLUCINATION_COPYPASTE`). The fallback banner reads `LOCAL_DETERMINISTIC_CACHE` and that is fine to show — it is a feature, not a glitch.
2. **Dark mode, high contrast.** Dark UI, Inter for prose, Geist Mono for JSON panels and scores. Judge legibility on a phone-sized window before the final take.
3. **Start with the problem hook.** Zero seconds of logo, team names, or "hi we are team X". The first frame is the problem. Introductions, if they happen at all, belong in the deck.
4. **Record the flow in order.** Intake → checklist → syllabus → reader → interview → report. Do not jump-cut into the middle of the pipeline; the gate only reads as a gate if the viewer watched the lock close.
5. **One number per claim, sourced.** If a figure is not in the Evidence Card above, it does not go in the video.
6. **Record the rejection path first.** The honest-rejection take is the one that wins; the copypaste-caught take is the punchline. Both must be in the same recording session so the UI state matches.
