# ai/ — Function Fixtures

Example output for every function in `ai/__init__.py`, copied from
`docs/architecture/API-CONTRACTS.md` v2 so DEV 2 can wire routes before the engine is finished
(DEV3-ROADMAP section 1). The shapes here are the contract — if the code disagrees, the
contract wins.

All examples assume a Frontend / React intent. In `DEMO_MODE=cached` (or with no key)
every function returns these deterministic shapes.

## classify_intent(intent) -> dict
```json
{ "role_guess": "Frontend", "suggested_others": false, "confidence": 0.9 }
```

## gen_checklist(intent, role, doc_text, stream=False) -> list[dict]
```json
[
  { "item_id": "ck_01", "topic": "Reconciliation & Fiber tree", "selected": true, "confidence": 0.92, "origin": "document" },
  { "item_id": "ck_02", "topic": "Scheduling & priority lanes", "selected": true, "confidence": 0.88, "origin": "role_taxonomy" }
]
```
`stream=True` returns an iterator of the same items (SSE `checklist.partial`).
`origin` ∈ `document` | `role_taxonomy` | `grounded_external`.

## index_document(pdf_bytes) -> dict
```json
{ "pages": [{ "page": 1, "text": "..." }], "chunks": [{ "page": 1, "text": "..." }], "total_pages": 3 }
```

## synth_syllabus(intent, role, doc_index, enable_search_grounding) -> dict
```json
{
  "syllabus_id": "syl_9f8e",
  "title": "Frontend Deep Dive: React Internals",
  "source_mode": "document_rag",
  "total_chapters": 2,
  "chapters": [
    { "chapter_id": "ch_01", "title": "Virtual DOM vs Real DOM", "order": 1, "status": "ACTIVE_READING",
      "prerequisites": [], "estimated_reading_minutes": 4, "objectives": ["..."],
      "source_pages": [3, 4, 5],
      "references": [{ "kind": "document", "label": "Uploaded PDF", "page": 4, "verified": true }] },
    { "chapter_id": "ch_02", "title": "Fiber Reconciler & Scheduling", "order": 2, "status": "LOCKED",
      "prerequisites": ["ch_01"], "estimated_reading_minutes": 6, "objectives": ["..."],
      "source_pages": [6, 7, 8],
      "references": [{ "kind": "document", "label": "Uploaded PDF", "page": 7, "verified": true },
                     { "kind": "grounded_external", "label": "react.dev — Reconciler", "url": "https://react.dev/...", "cached": true }] }
  ]
}
```
`source_mode` ∈ `document_rag` | `role_taxonomy_generated`. The no-PDF path yields
`role_taxonomy_generated` with empty `source_pages`.

## socratic_ask(chapter, selected_text, question, anchor) -> dict
```json
{ "mode": "socratic",
  "reply": "Before I answer — what do you think would happen if React had no such process?",
  "hint_level": 1, "citations": [{ "kind": "document", "page": 4 }], "gave_direct_answer": false }
```
`gave_direct_answer` is always `false` in default mode.

## suggest_questions(chapter, selection) -> list[str]
```json
["Why is O(n) diffing considered good enough for React?",
 "How does reconciliation differ from the commit phase?",
 "When does diffing actually become the bottleneck?"]
```

## start_interview(chapter) -> dict
```json
{ "interview_id": "int_7712", "chapter_id": "ch_01", "turn_index": 1,
  "first_question": "When does the Virtual DOM actually become a bottleneck?",
  "focus_mode": { "required": false, "available": true } }
```

## interview_turn(interview, user_response, client_telemetry) -> dict
```json
{ "interview_id": "int_7712", "turn_index": 2, "is_concluded": false, "running_score": 78,
  "interrogator_response": "Solid. Now, how would you apply the 'React Quantum Hook'...",
  "honeypot_active": true,
  "honeypot_metadata": { "injected_term": "React Quantum Hook",
                         "expected_action": "REJECT_AS_FICTITIOUS", "source": "deterministic_catalog" } }
```

## finalize_interview(interview, final_response, session_used_terms) -> dict
```json
{ "interview_id": "int_7712", "chapter_id": "ch_01", "passed": true,
  "score": { "chapter_score": 88, "reasoning_score": 92, "integrity_score": 100, "honeypot_score": 2 },
  "honeypot_verdict": { "term": "React Quantum Hook", "result": "CRITICAL_REJECTION", "analysis": "..." },
  "chapter_state_update": { "current_chapter_status": "UNLOCKED", "next_unlocked_chapter_id": "ch_02" },
  "verifier": { "status": "agreed", "note": "Second model agreed." } }
```

## pick_honeypot_term(chapter_topic, used, seed=None) -> dict
```json
{ "term": "React Quantum Hook", "catalog_id": "hp_react_quantum_hook",
  "category": "Frontend/React", "source": "deterministic_catalog",
  "expected_action": "REJECT_AS_FICTITIOUS" }
```

## classify_honeypot(user_response, term) -> dict
```json
{ "result": "CRITICAL_REJECTION", "points": 2, "analysis": "Student identified and critically rejected the fictitious premise." }
```
Class → points (frozen, ADR 002): `CRITICAL_REJECTION` +2, `AI_HALLUCINATION_COPYPASTE` −2,
`UNVERIFIED_HONEST` 0, `EVASIVE` −1.

## score_chapter(reasoning_score, integrity_score, honeypot_points, integrity_flag) -> dict
```json
{ "chapter_score": 88, "reasoning_score": 92, "integrity_score": 100, "honeypot_score": 2 }
```
Formula (ADR 002): `chapter_score = clamp(reasoning_score + honeypot_points + integrity_adjustment, 0, 100)`,
`integrity_adjustment` = `{clean: 0, assisted: -3, assisted_unverified: 0}`.

## calibration_label(predicted, actual) -> dict
```json
{ "calibration_gap": 2, "label": "well_calibrated" }
```
`label`: `overconfident` (predicted > actual + 15), `underconfident` (predicted < actual − 15),
`well_calibrated`.

## verify_score(score, evidence) -> dict
```json
{ "status": "agreed", "note": "Second model agreed." }
```
`status` ∈ `agreed` | `uncertain`.
