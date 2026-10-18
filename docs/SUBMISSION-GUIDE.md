# Assay — Submission Readiness Guide

> **Event:** AI Builder Cup 2026 (Google Cloud × Hack2skill, JAPAC)  
> **Track:** Track 4 — Media, Content & Digital Experiences (Adaptive Learning)  
> **Submission Deadline:** 18 October 2026, 23:59 UTC+8  
> **Positioning:** *Every AI study tool answers questions. Assay interrogates your answers.*  

---

## 1. Submission Deliverables Summary

| Deliverable | Format | Destination | Key Requirements |
| :--- | :--- | :--- | :--- |
| **1. Demo Video** | `.mp4` / YouTube unlisted | Hack2skill portal | **180s hard cap (3 minutes)**, 1080p, English voiceover, dry technical tone, zero logos/intro slides at start. |
| **2. Pitch Deck** | PDF (16:9) | Hack2skill portal | **10 Slides**, English, backed by empirical data from `docs/PITCH-DECK-OUTLINE.md`. |
| **3. Code Repository** | Public GitHub / GitLab | Hack2skill portal | Clean fullstack repo, passing tests (253/253: 223 backend + 25 engine + 5 eval), architecture diagram, `.env.example`. |

---

## 2. 3-Minute Video Recording Storyboard (Strict 180s)

Follow this exact second-by-second script when recording your screen:

```
[00:00 - 00:20] THE HOOK
Visual: Drop PDF into ChatGPT, click "Summarize", fast scroll. Cut to stat card.
Voiceover: "95% of students use AI. 67% say it harms their critical thinking. The tool answers instantly — and reasoning collapses on the first edge case."

[00:20 - 00:50] INTAKE (http://localhost:5173/app/intake)
Visual: Enter intent: "Decision Theory & Likelihood Ratio Testing". Select "Data/ML". Show no "Summarize" button exists.
Voiceover: "This is Assay. It does not summarize. It generates an active inquiry roadmap from your intent and role taxonomy."

[00:50 - 01:15] REALTIME CHECKLIST
Visual: Curate checklist items, uncheck one item, click Generate Syllabus.
Voiceover: "The checklist streams live. You decide what becomes chapters. The syllabus belongs to you, not the model."

[01:15 - 01:40] SYLLABUS GATING
Visual: Show 4 chapters. Chapter 1 is ACTIVE, Chapter 2 is visibly LOCKED.
Voiceover: "Assay locks successive chapters. You cannot skip ahead without defending your grasp."

[01:40 - 02:05] GATED DEEP READER (http://localhost:5173/app/reader)
Visual: Highlight "unobserved counterfactual" -> Socratic popover opens with counter-question. Show LaTeX formula and Figure 3.1 sample space partition curve.
Voiceover: "Highlight any term and ask. Assay never gives away the answer — gave_direct_answer is false. It forces deduction."

[02:05 - 02:45] ORAL DEFENSE & HONEYPOT (http://localhost:5173/app/exam/ch_01)
Visual: Dr. Julian Vance oral exam. Click microphone -> waveform moves. Fallacy probe appears: "Quantum Bayesian Shrinkage".
Visual: Candidate rejects the fictional concept -> score +2 CRITICAL_REJECTION.
Voiceover: "Every chapter ends in oral defense. Assay injects fictional concepts — honeypots. Generic LLMs hallucinate 54% of the time. Rejecting the trap awards +2; copy-pasting incurs -2."

[02:45 - 03:00] VERDICT & REPORT (http://localhost:5173/app/report)
Visual: Score 92/100 -> Chapter 2 UNLOCKS. Show 5-Axis Bloom Taxonomy Radar Spider Chart and SHA-256 Audit Record.
Voiceover: "Exceeding the threshold unlocks the next module. The final report maps your 5-axis Bloom profile and signs it with cryptographic attestation. Thank you."
```

---

## 3. How to Record the Demo Video on Windows

1. **Option A (Screen Studio / Canvid / Cap - Best Quality)**:
   - Use [Cap.so](https://cap.so/) or [Canvid](https://www.canvid.com/) for automatic zoom-on-click and high-contrast styling.
2. **Option B (Windows Game Bar - Instant Built-in)**:
   - Press `Win + Alt + R` to start/stop recording.
   - Microphone voiceover is recorded directly.
3. **Golden Rule**:
   - Keep `DEMO_MODE=live` if internet and API key are stable.
   - If internet is jittery during recording, set `DEMO_MODE=cached` — **never let a spinner freeze on camera**.

---

## 4. Local Test & Verification Runbook

```powershell
# Terminal 1: Backend
cd D:\Lab\nexatriv\ai-builder-cup\assay\backend
.\venv\Scripts\Activate.ps1
uvicorn app.main:app --reload --port 8000

# Terminal 2: Frontend
cd D:\Lab\nexatriv\ai-builder-cup\assay\frontend
npm run dev
```

Visit:
- `http://localhost:5173/app/dashboard`
- `http://localhost:5173/app/settings` (Click "Test Mic" to verify audio input)
- `http://localhost:5173/app/reader` (Test KaTeX and Socratic asking)
- `http://localhost:5173/app/exam/ch_01` (Test voice oral defense with examiner TTS)
- `http://localhost:5173/app/report` (Test Bloom radar chart and audit hash)
