# API & Data Contracts Specification — v2.0.0
## Assay: The Active Socratic Learning Engine

**Status:** LOCKED CONTRACT (Freeze Date: 14 Oktober 2026)
**Standard:** REST + Server-Sent Events (SSE) / JSON Schema
**Base URL:** `/api/v1`
**Supersedes:** API-CONTRACTS v1 (state `LOCKED→ACTIVE_READING→INTERROGATE`; endpoint `modules/ingest`)

> Semua endpoint di dokumen ini adalah kontrak antar-dev. Frontend tidak menunggu backend — pakai mock dari contoh JSON di sini.

---

## 0. Perubahan dari v1

| v1 | v2 | Alasan |
|---|---|---|
| `POST /modules/ingest` (PDF/teks → node) | `POST /intake`, `POST /intake/:id/checklist`, `POST /intake/:id/syllabus` | Flow baru: intent + role + PDF opsional |
| State `LOCKED→ACTIVE_READING→INTERROGATE→UNLOCKED` | `LOCKED→ACTIVE_READING→INTERVIEW→SCORED→UNLOCKED/NEEDS_REVIEW` | Hapus `DEBUG_CHALLENGE` (TDL dicut) |
| `POST /interrogate/turn`, `/interrogate/finalize` | `POST /chapters/:id/interview/turn`, `/chapters/:id/interview/finalize` | Per-chapter, bukan per-node |
| (tidak ada) | `POST /chapters/:id/ask`, `GET /chapters/:id/suggestions` | Select-word → tanya AI (Socratic) |
| (tidak ada) | `POST /chapters/:id/calibration` | Calibration "predict before reveal" |
| (tidak ada) | `POST /chapters/:id/focus-events` | Focus Mode (MediaPipe events) |
| (tidak ada) | `POST /chapters/:id/appeal`, `GET /report/:session_id` | Appeal + final report |
| `DEMO_MODE=cached` env saja | env `DEMO_MODE=cached` **atau** header `x-demo-mode: cached` | v1 beda trigger di 2 dokumen |
| honeypot enum 3 nilai | 4 nilai (+`EVASIVE`) + skor ± | Riset A1 |

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

Honeypot **tidak** mengubah state — dia hanya mengisi `honeypot_score` di dalam skor.

---

## 2. Endpoints

### 2.1 Intake
#### `POST /api/v1/intake`
Menerima niat belajar + role + PDF opsional. Mengembalikan `session_id` + daftar role seed.

* **Request (multipart/form-data atau JSON):**
```json
{
  "intent": "I want to understand how React rendering works internally",
  "role": "Frontend",
  "role_is_custom": false,
  "document": null
}
```
`role` harus salah satu dari seed (`GET /roles`) atau `"Others"` dengan `role_is_custom: true` + `custom_role` terisi.

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
Daftar role seed (buat render selector).
```json
{
  "roles": ["Frontend","Backend","Fullstack","DevOps","Data/ML","Mobile","QA/Test","Security","System Design"],
  "others_option": "Others"
}
```

---

### 2.2 Realtime Checklist Generation
#### `POST /api/v1/intake/:sessionId/checklist`
Generate checklist topik realtime dari intent + role + isi PDF (kalau ada).

* **Request:** `{}` (pakai state intake) atau override:
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

* **SSE variant (`stream: true`):** event `checklist.partial` per item, lalu `checklist.done`.

#### `PUT /api/v1/intake/:sessionId/checklist`
User finalisasi pilihan (check/uncheck).
```json
{ "selected_item_ids": ["ck_01","ck_02"] }
```

---

### 2.3 Syllabus Synthesis
#### `POST /api/v1/intake/:sessionId/syllabus`
Chunk dokumen (atau generate dari role taxonomy) jadi chapter silabus + enrich referensi.

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
Grounding eksternal: `enable_search_grounding: true` cuma buat 1-2 chapter, hasil di-cache (lihat §3).

---

### 2.4 Chapter Reader & Inline Socratic Ask
#### `GET /api/v1/chapters/:chapterId`
Konten chapter + state.

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
User select kata/kalimat → tanya AI. **AI menjawab Socratic** (balik nanya / hint), bukan jawaban jadi.

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
  "reply": "Sebelum gw jawab — menurut kamu, kalau React nggak punya proses ini, apa yang bakal terjadi ke DOM tiap state berubah?",
  "hint_level": 1,
  "citations": [{ "kind": "document", "page": 4 }],
  "gave_direct_answer": false
}
```
`gave_direct_answer` harus `false` di mode default (konsistensi tesis "anti brain-rot").

#### `GET /api/v1/chapters/:chapterId/suggestions?selection=...`
AI kasih suggested questions dari seleksi beberapa kata.
```json
{
  "selection": "reconciliation and diffing",
  "suggested_questions": [
    "Kenapa diffing O(n) dianggap cukup buat React?",
    "Apa bedanya reconciliation sama commit phase?",
    "Kapan diffing justru jadi bottleneck?"
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
  "first_question": "Bayangkan kamu punya 10.000 list item yang diupdate tiap 100ms. Kapan Virtual DOM justru jadi bottleneck dibanding manipulasi DOM langsung?",
  "focus_mode": { "required": false, "available": true }
}
```

#### `POST /api/v1/chapters/:chapterId/interview/turn`
* **Request:**
```json
{
  "interview_id": "int_7712",
  "turn_index": 1,
  "user_response": "VDOM jadi bottleneck karena diffing pohon 10.000 objek JS sendiri butuh CPU cycle...",
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
  "interrogator_response": "Solid. Sekarang, bagaimana penerapan 'React Quantum Hook' dalam mengatasi mutasi state 100ms itu? Apakah tepat?",
  "honeypot_active": true,
  "honeypot_metadata": {
    "injected_term": "React Quantum Hook",
    "expected_action": "REJECT_AS_FICTITIOUS",
    "source": "deterministic_catalog"
  }
}
```

#### `POST /api/v1/chapters/:chapterId/interview/finalize`
Hitung skor chapter. **Sebelum** ini, user isi calibration (§2.6).

* **Request:**
```json
{
  "interview_id": "int_7712",
  "final_response": "Setahu saya 'React Quantum Hook' gak ada di React docs maupun library resmi. Yang ada useTransition atau useDeferredValue."
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
    "analysis": "User menyadari dan menolak istilah fiktif."
  },
  "chapter_state_update": { "current_chapter_status": "UNLOCKED", "next_unlocked_chapter_id": "ch_02" },
  "verifier": { "status": "agreed", "note": "Model kedua setuju." }
}
```

**Klasifikasi honeypot → skor (ADR 002 + riset A1):**
| `result` | Arti | Skor |
|---|---|---|
| `CRITICAL_REJECTION` | Curiga & tepat | **+2** |
| `AI_HALLUCINATION_COPYPASTE` | Panjang, yakin, halusinasi | **−2** |
| `UNVERIFIED_HONEST` | "gw gak tau" | **0** |
| `EVASIVE` | Diam/muter gak nyerempet | **−1** |

Honeypot **bukan** gate. Unlock tetap dari `chapter_score >= 75`.

---

### 2.6 Calibration
#### `POST /api/v1/chapters/:chapterId/calibration`
User memprediksi skor dirinya **sebelum** reveal.

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
On-device ML kirim **event boolean** (bukan video).

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
`video_transmitted` **wajib** `false` (privasi — ADR 003).
**Accessible Mode** (kamera off) → `integrity_flag: "assisted_unverified"`, skor tetap dihitung.

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

Trigger: env `DEMO_MODE=cached` **ATAU** header `x-demo-mode: cached` **ATAU** Gemini error `429/500/503`.

Sistem backend **wajib** menyajikan skenario pre-cached tanpa runtime exception:
```json
{ "fallback_active": true, "source": "LOCAL_DETERMINISTIC_CACHE", "message": "(Offline simulation active — Gemini mocked for resilience)" }
```

Skenario wajib:
1. **Success flow** — user kritis nolak honeypot → `CRITICAL_REJECTION`, skor tinggi, chapter unlock.
2. **Caught flow** — user copas jawaban LLM luar → `AI_HALLUCINATION_COPYPASTE`, skor turun, flag integrity.

Cache juga menyimpan hasil grounding eksternal (biar demo gak gantung ke jaringan).

---

## 4. Structured Output Schema (Gemini)
Semua evaluasi pakai JSON schema (native structured output):
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
