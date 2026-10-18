# API & Data Contracts Specification — v2.0.0
## Assay: The Active Socratic Learning Engine

**Status:** LOCKED CONTRACT (Freeze Date: 14 October 2026)
**Standard:** REST + Server-Sent Events (SSE) / JSON Schema
**Base URL:** `/api/v1`
**Supersedes:** API-CONTRACTS v1 (state `LOCKED→ACTIVE_READING→INTERROGATE`; endpoint `modules/ingest`)

> Every endpoint in this document is a cross-team contract. The frontend does not wait on the backend — use the mocks from the JSON examples here.

---

## 0. Changes from v1

| v1 | v2 | Reason |
|---|---|---|
| `POST /modules/ingest` (PDF/teks → node) | `POST /intake`, `POST /intake/:id/checklist`, `POST /intake/:id/syllabus` | New flow: intent + role + optional PDF |
| State `LOCKED→ACTIVE_READING→INTERROGATE→UNLOCKED` | `LOCKED→ACTIVE_READING→INTERVIEW→SCORED→UNLOCKED/NEEDS_REVIEW` | Removed `DEBUG_CHALLENGE` (TDL cut) |
| `POST /interrogate/turn`, `/interrogate/finalize` | `POST /chapters/:id/interview/turn`, `/chapters/:id/interview/finalize` | Per-chapter, not per-node |
| (none) | `POST /chapters/:id/ask`, `GET /chapters/:id/suggestions` | Select-word → ask AI (Socratic) |
| (none) | `POST /chapters/:id/calibration` | Calibration "predict before reveal" |
| (none) | `POST /chapters/:id/focus-events` | Focus Mode (MediaPipe events) |
| (none) | `POST /chapters/:id/appeal`, `GET /report/:session_id` | Appeal + final report |
| `DEMO_MODE=cached` env only | env `DEMO_MODE=cached` **or** header `x-demo-mode: cached` | v1 used different triggers across 2 documents |
| honeypot enum 3 values | 4 values (+`EVASIVE`) + ± score | Research A1 |

---

## 1. Chapter Lifecycle State Machine

```
┌──────────┐   Open chapter (prev UNLOCKED)   ┌────────────────┐
│  LOCKED  │ ───────────────────────────────> │ ACTIVE_READING │
└──────────┘                                  └───────┬────────┘
                                                      │ User starts interview quiz
                                                      ▼
                                              ┌────────────────┐
                                              │   INTERVIEW    │ <─── multi-turn
                                              │  (Socratic +   │      honeypot +
                                              │   Honeypot)    │      focus events
                                              └───────┬────────┘
                                                      │ finalize
                                                      ▼
                                              ┌────────────────┐
                                              │     SCORED     │
                                              └───────┬────────┘
                              score >= 75             │             score < 75
                    ┌─────────────────────────────────┴───────────────────────┐
                    ▼                                                          ▼
             ┌─────────────┐                                            ┌──────────────┐
             │  UNLOCKED   │                                            │ NEEDS_REVIEW │
             │ (Completed) │                                            │  (Retry)     │
             └─────────────┘                                            └──────────────┘
```

The honeypot does **not** change state — it only fills `honeypot_score` inside the score.

---

## 2. Endpoints

### 2.1 Intake
#### `POST /api/v1/intake`
Accepts the learning intent + role + optional PDF. Returns `session_id` + the list of seed roles.

* **Request (multipart/form-data or JSON):**
```json
{
  "intent": "I want to understand how React rendering works internally",
  "role": "Frontend",
  "role_is_custom": false,
  "document": null
}
```
`role` must be one of the seeds (`GET /roles`) or `"Others"` with `role_is_custom: true` + `custom_role` populated.

* **Response (201 Created):**
```json
{
  "session_id": "sess_a1b2c3",
  "intent": "I want to understand how React rendering works internally",
  "role": "Frontend",
  "has_document": false,
  "available_roles": ["Frontend","Backend","Fullstack","DevOps","Data/ML","Mobile","QA/Test","Security","System Design"],
  "suggested_others": false,
  "next": "POST /api/v1/intake/sess_a1b2c3/checklist"
}
```

#### `GET /api/v1/roles`
List of seed roles (for rendering the selector).
```json
{
  "roles": ["Frontend","Backend","Fullstack","DevOps","Data/ML","Mobile","QA/Test","Security","System Design"],
  "others_option": "Others"
}
```

---

### 2.2 Realtime Checklist Generation
#### `POST /api/v1/intake/:sessionId/checklist`
Generates a realtime topic checklist from the intent + role + PDF content (if any).

* **Request:** `{}` (uses intake state) or an override:
```json
{ "stream": true }
```

* **Response (200 OK):**
```json
{
  "session_id": "sess_a1b2c3",
  "role": "Frontend",
  "source": "document+role",
  "checklist": [
    { "item_id": "ck_01", "topic": "Reconciliation & Fiber tree", "selected": true, "confidence": 0.92, "origin": "document" },
    { "item_id": "ck_02", "topic": "Scheduling & priority lanes", "selected": true, "confidence": 0.88, "origin": "role_taxonomy" },
    { "item_id": "ck_03", "topic": "State batching semantics", "selected": false, "confidence": 0.71, "origin": "document" }
  ]
}
```
`origin`: `document` | `role_taxonomy` | `grounded_external`.

* **SSE variant (`stream: true`):** a `checklist.partial` event per item, then `checklist.done`.

#### `PUT /api/v1/intake/:sessionId/checklist`
The user finalizes their selection (check/uncheck).
```json
{ "selected_item_ids": ["ck_01","ck_02"] }
```

---

### 2.3 Syllabus Synthesis
#### `POST /api/v1/intake/:sessionId/syllabus`
Chunks the document (or generates from the role taxonomy) into syllabus chapters + enriches references.

* **Request:**
```json
{ "enable_search_grounding": false }
```

* **Response (201 Created):**
```json
{
  "session_id": "sess_a1b2c3",
  "syllabus_id": "syl_9f8e",
  "title": "Frontend Deep Dive: React Internals",
  "source_mode": "document_rag",
  "total_chapters": 3,
  "chapters": [
    {
      "chapter_id": "ch_01",
      "title": "Virtual DOM vs Real DOM",
      "order": 1,
      "status": "ACTIVE_READING",
      "prerequisites": [],
      "estimated_reading_minutes": 4,
      "source_pages": [3, 4, 5],
      "references": [
        { "kind": "document", "label": "Uploaded PDF", "page": 4, "verified": true }
      ]
    },
    {
      "chapter_id": "ch_02",
      "title": "Fiber Reconciler & Scheduling",
      "order": 2,
      "status": "LOCKED",
      "prerequisites": ["ch_01"],
      "estimated_reading_minutes": 6,
      "source_pages": [6, 7, 8],
      "references": [
        { "kind": "document", "label": "Uploaded PDF", "page": 7, "verified": true },
        { "kind": "grounded_external", "label": "react.dev — Reconciler", "url": "https://react.dev/...", "cached": true }
      ]
    }
  ]
}
```
`source_mode`: `document_rag` | `role_taxonomy_generated`.
External grounding: `enable_search_grounding: true` only for 1-2 chapters, results are cached (see §3).

---

### 2.4 Chapter Reader & Inline Socratic Ask
#### `GET /api/v1/chapters/:chapterId`
Chapter content + state.

* **Response (200 OK):**
```json
{
  "chapter_id": "ch_01",
  "title": "Virtual DOM vs Real DOM",
  "status": "ACTIVE_READING",
  "content_markdown": "## Virtual DOM ...",
  "source_pages": [3,4,5],
  "next_locked": true,
  "interview_available": true
}
```

#### `POST /api/v1/chapters/:chapterId/ask`
The user selects a word/sentence → asks the AI. **The AI answers Socratically** (asks back / gives a hint), not with a finished answer.

* **Request:**
```json
{
  "session_id": "sess_a1b2c3",
  "selected_text": "reconciliation",
  "question": "What does this actually do?",
  "anchor": { "page": 4, "char_start": 812, "char_end": 826 }
}
```

* **Response (200 OK):**
```json
{
  "mode": "socratic",
  "reply": "Before I answer — what do you think would happen to the DOM on every state change if React had no such process?",
  "hint_level": 1,
  "citations": [{ "kind": "document", "page": 4 }],
  "gave_direct_answer": false
}
```
`gave_direct_answer` must be `false` in the default mode (consistency with the "anti brain-rot" thesis).

#### `GET /api/v1/chapters/:chapterId/suggestions?selection=...`
The AI provides suggested questions from a selection of several words.
```json
{
  "selection": "reconciliation and diffing",
  "suggested_questions": [
    "Why is O(n) diffing considered good enough for React?",
    "What is the difference between the reconciliation and commit phases?",
    "When does diffing actually become the bottleneck?"
  ]
}
```

---

### 2.5 Interview Quiz & Honeypot
#### `POST /api/v1/chapters/:chapterId/interview/start`
```json
{ "session_id": "sess_a1b2c3" }
```
* **Response (200 OK):**
```json
{
  "interview_id": "int_7712",
  "chapter_id": "ch_01",
  "turn_index": 1,
  "first_question": "Imagine 10,000 list items updating every 100ms. At what point does the Virtual DOM become the bottleneck compared to direct DOM manipulation?",
  "focus_mode": { "required": false, "available": true }
}
```

#### `POST /api/v1/chapters/:chapterId/interview/turn`
* **Request:**
```json
{
  "interview_id": "int_7712",
  "turn_index": 1,
  "user_response": "The VDOM becomes the bottleneck because diffing a tree of 10,000 JS objects costs CPU cycles on its own...",
  "client_telemetry": { "paste_detected": false, "duration_seconds": 38, "keystroke_cpm": 260 }
}
```

* **Response (200 OK):**
```json
{
  "interview_id": "int_7712",
  "turn_index": 2,
  "is_concluded": false,
  "running_score": 78,
  "interrogator_response": "Solid. Now, how does applying 'React Quantum Hook' address that 100ms state mutation? Is that the right fit?",
  "honeypot_active": true,
  "honeypot_metadata": {
    "injected_term": "React Quantum Hook",
    "expected_action": "REJECT_AS_FICTITIOUS",
    "source": "deterministic_catalog"
  }
}
```

#### `POST /api/v1/chapters/:chapterId/interview/finalize`
Computes the chapter score. **Before** this call, the user fills in the calibration (§2.6).

* **Request:**
```json
{
  "interview_id": "int_7712",
  "final_response": "As far as I know 'React Quantum Hook' does not exist in the React docs or any official library. What exists is useTransition or useDeferredValue.",
}
```

* **Response (200 OK):**
```json
{
  "interview_id": "int_7712",
  "chapter_id": "ch_01",
  "passed": true,
  "score": { "chapter_score": 88, "reasoning_score": 92, "integrity_score": 100, "honeypot_score": 2 },
  "honeypot_verdict": {
    "term": "React Quantum Hook",
    "result": "CRITICAL_REJECTION",
    "analysis": "User recognized and rejected the fabricated term."
  },
  "chapter_state_update": { "current_chapter_status": "UNLOCKED", "next_unlocked_chapter_id": "ch_02" },
  "verifier": { "status": "agreed", "note": "Model kedua setuju." }
}
```

**Honeypot classification → score (ADR 002 + research A1):**
| `result` | Meaning | Score |
|---|---|---|
| `CRITICAL_REJECTION` | Suspicious & correct | **+2** |
| `AI_HALLUCINATION_COPYPASTE` | Long, confident, hallucinated | **−2** |
| `UNVERIFIED_HONEST` | "I don't know" | **0** |
| `EVASIVE` | Silent/dodging, never lands | **−1** |

The honeypot is **not** a gate. Unlock still comes from `chapter_score >= 75`.

---

### 2.6 Calibration
#### `POST /api/v1/chapters/:chapterId/calibration`
The user predicts their own score **before** the reveal.

* **Request:**
```json
{ "interview_id": "int_7712", "predicted_score": 90 }
```

* **Response (200 OK):**
```json
{
  "predicted_score": 90,
  "actual_score": 88,
  "calibration_gap": 2,
  "label": "well_calibrated"
}
```
`label`: `overconfident` (predicted > actual + 15), `underconfident` (predicted < actual − 15), `well_calibrated`.

---

### 2.7 Focus Mode (MediaPipe events)
#### `POST /api/v1/chapters/:chapterId/focus-events`
On-device ML sends **boolean events** (not video).

* **Request:**
```json
{
  "interview_id": "int_7712",
  "events": [
    { "type": "GAZE_DRIFT", "at_ms": 41200, "duration_ms": 6200 },
    { "type": "MULTIPLE_FACES", "at_ms": 51000, "count": 2 },
    { "type": "TAB_BLUR", "at_ms": 60000, "duration_ms": 15000 }
  ],
  "video_transmitted": false
}
```

* **Response (200 OK):**
```json
{
  "integrity_flag": "assisted",
  "auto_blur": true,
  "summary": { "gaze_drift_count": 1, "multi_face_count": 1, "tab_blur_count": 1 }
}
```

`type` enum: `GAZE_DRIFT` | `MULTIPLE_FACES` | `TAB_BLUR` | `CAMERA_OFF`.
`video_transmitted` **must** be `false` (privacy — ADR 003).
**Accessible Mode** (camera off) → `integrity_flag: "assisted_unverified"`, the score is still computed.

---

### 2.8 Appeal & Final Report
#### `POST /api/v1/chapters/:chapterId/appeal`
```json
{ "interview_id": "int_7712", "reason": "Jawaban saya singkat tapi tepat; skor terasa terlalu rendah." }
```
* **Response (200 OK):**
```json
{ "appeal_id": "apl_22", "status": "under_review", "reviewer": "verifier_model", "possible_outcome": ["upheld","revised","uncertain"] }
```

#### `GET /api/v1/report/:sessionId`
```json
{
  "session_id": "sess_a1b2c3",
  "syllabus_title": "Frontend Deep Dive: React Internals",
  "chapters": [
    { "chapter_id": "ch_01", "status": "UNLOCKED", "score": 88, "calibration_gap": 2, "integrity": "clean" },
    { "chapter_id": "ch_02", "status": "NEEDS_REVIEW", "score": 62, "calibration_gap": 28, "integrity": "assisted" }
  ],
  "summary": {
    "mean_score": 75,
    "mean_calibration_gap": 15,
    "integrity_flags": 1,
    "honeypot_verdicts": { "CRITICAL_REJECTION": 1, "UNVERIFIED_HONEST": 1 }
  }
}
```

---

## 3. Resilient Fallback Specification

Trigger: env `DEMO_MODE=cached` **OR** header `x-demo-mode: cached` **OR** Gemini error `429/500/503`.

The backend **must** serve pre-cached scenarios without runtime exceptions:
```json
{ "fallback_active": true, "source": "LOCAL_DETERMINISTIC_CACHE", "message": "(Offline simulation active — Gemini mocked for resilience)" }
```

Required scenarios:
1. **Success flow** — a critical user rejects the honeypot → `CRITICAL_REJECTION`, high score, chapter unlocked.
2. **Caught flow** — a user pastes an answer from an external LLM → `AI_HALLUCINATION_COPYPASTE`, score drops, integrity flag raised.

The cache also stores external grounding results (so the demo doesn't depend on the network).

---

## 4. Structured Output Schema (Gemini)
All evaluations use a JSON schema (native structured output):
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "chapter_score": { "type": "integer", "minimum": 0, "maximum": 100 },
    "reasoning_score": { "type": "integer", "minimum": 0, "maximum": 100 },
    "honeypot_result": {
      "type": "string",
      "enum": ["CRITICAL_REJECTION","AI_HALLUCINATION_COPYPASTE","UNVERIFIED_HONEST","EVASIVE","NONE"]
    },
    "misconceptions": { "type": "array", "items": { "type": "string" } },
    "evidence_quotes": { "type": "array", "items": { "type": "string" } },
    "socratic_feedback": { "type": "string" },
    "follow_up_question": { "type": "string" },
    "confidence": { "type": "number", "minimum": 0, "maximum": 1 }
  },
  "required": ["chapter_score","reasoning_score","honeypot_result","socratic_feedback","confidence"]
}
```
