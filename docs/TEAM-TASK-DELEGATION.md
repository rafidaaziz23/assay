# Team Work Breakdown Structure (WBS) & Sprint Delegation — v2.0.0
## Assay: The Active Socratic Learning Engine — 4-Day Rapid Prototype Sprint (14 – 18 Oktober 2026)

**Submission Deadline:** 18 Oktober 2026, 23:59 UTC+8 — **HARD DEADLINE** (submit target: 20:00 UTC+8)
**Squad Size:** 3 Developers (full parallel execution)
**Core Motto:** "Contract-First, Zero Blocker, Demo Reliability Above All"
**Dokumen ini menggantikan** WBS v1 (CogniForge, 4-dev, TDL + Monaco + DAG Skill Tree). Semua task di v1 yang menyebut `modules/ingest`, `interrogate/turn`, Dual-Metric Score Card, atau TDL **batal** — lihat §0.

---

## 0. Sumber Kebenaran & Cara Baca Dokumen Ini

Urutan otoritas kalau ada konflik antar dokumen:

1. [PRD.md](./PRD.md) v2.0.0 §3 (Core User Flow — KANONIK) dan §5 (alokasi tim) / §6 (timeline) / §8 (non-goals).
2. [API-CONTRACTS.md](./API-CONTRACTS.md) v2.0.0 — LOCKED CONTRACT (freeze 14 Okt). Sumber tunggal endpoint + schema + state machine.
3. Dokumen ini — pembagian kerja, urutan hari, gate per hari.

| Dokumen | Fungsi | Link |
|---|---|---|
| PRD v2.0.0 | Flow kanonik, rubrik, non-goals | [./PRD.md](./PRD.md) |
| API-CONTRACTS v2.0.0 | Endpoint, JSON, state machine | [./API-CONTRACTS.md](./API-CONTRACTS.md) |
| Demo script | Storyboard video 3 menit | [./DEMO-SCRIPT.md](./DEMO-SCRIPT.md) |
| Pitch deck outline | 10 slide bahasa Inggris | [./PITCH-DECK-OUTLINE.md](./PITCH-DECK-OUTLINE.md) |
| Audit + Q&A juri | Jawaban juri, SWOT, threat | [./AUDIT.md](./AUDIT.md) |
| ADR 001 | Model routing Flash vs Pro | [./docs/adrs/001-model-selection.md](./docs/adrs/001-model-selection.md) |
| ADR 002 | Deterministic honeypot guardrails | [./docs/adrs/002-deterministic-honeypot-guardrails.md](./docs/adrs/002-deterministic-honeypot-guardrails.md) |
| ADR 003–005 | MediaPipe client-side, role taxonomy seed, honeypot katalog+variasi — **belum ada filenya**, DEV 3 tulis sesuai PRD §11 | `docs/adrs/` (TODO) |
| Angka empiris | Honeypot, trap, verifier, JSON | [../reza-research/parts10/HASIL-TES-EMPIRIS.md](../reza-research/parts10/HASIL-TES-EMPIRIS.md) |
| Deadline resmi panitia | Bukti 18 Okt | [../01-event-guidelines/02-timeline-schedule.md](../01-event-guidelines/02-timeline-schedule.md) |

> Kalau ada dev yang nemu kontradiksi antar dokumen, **berhenti dan angkat di sync** — jangan pilih sendiri.

---

## 1. Reality Check: Kapasitas vs Beban (WAJIB DIBACA SEBELUM MULAI)

```
+--------------------------------------------------------------------------------+
|  KAPASITAS                          vs   BEBAN                                 |
+--------------------------------------------------------------------------------+
|  3 dev x 4 hari          = 12.0 dev-day    Flow baru (PRD §5)   = 11.25 d-day  |
|  overhead integrasi ~20% = -2.4 dev-day    Fitur wajib riset    =  3.50 d-day  |
|  ----------------------------------------  ----------------------------------- |
|  EFEKTIF                 =  9.6 dev-day    TOTAL KEBUTUHAN      = 14.75 d-day  |
|                                                                                |
|                     DEFISIT = 5.15 dev-day  -->  CUT ITU WAJIB                 |
+--------------------------------------------------------------------------------+
```

Angka di atas dari [PRD.md](./PRD.md) §5 dan §8, bukan estimasi baru. Ledger pemotongan:

| Blok | Sebelum cut | Aksi | Sesudah cut |
|---|---:|---|---:|
| Monaco + Piston + TDL (coding arena) | 1.50 | **CUT** → roadmap slide | 0.00 |
| DAG Skill Tree visual (ReactFlow) | 1.00 | **CUT** → chapter stepper linear | 0.00 |
| Dual-metric (Concept + Reasoning) | 0.50 | **CUT** → single score + calibration gap | 0.00 |
| Voice / Gemini Live | 0.50 | CUT → roadmap | 0.00 |
| Auth kompleks / multi-user | 0.25 | CUT → 1 session demo | 0.00 |
| Multi-source input (video/audio) | 0.25 | CUT → PDF + raw text | 0.00 |
| **Subtotal cut** | **4.00** | | **10.75** |
| Report view (chart → tabel) | 0.25 | Trim | |
| Appeal path (verifier penuh → stub status) | 0.25 | Trim | |
| Accessible Mode (penuh → 1 toggle) | 0.25 | Trim | |
| Grounding eksternal (2 chapter → 1 chapter, cached) | 0.25 | Trim | |
| Focus Mode (6 event → 3 event) | 0.15 | Trim | |
| **Subtotal trim** | **1.15** | | **9.60 = kapasitas efektif** |

**Jangan pernah di-cut** (PRD §8, ini yang nangkep Technical Merit 40%): eval harness + angka, verifier loop, calibration, cached fallback, honeypot, gate unlock ≥ 75.

Kalau ada ide fitur baru setelah Hari 0: **tulis di roadmap slide, jangan di repo.**

---

## 2. Alokasi Peran — 3 Developer

```
┌─────────────────────────────────┬─────────────────────────────────┬─────────────────────────────────┐
│ DEV 1: FRONTEND & UX            │ DEV 2: BACKEND & DATA           │ DEV 3: AI ENGINE & EVAL         │
├─────────────────────────────────┼─────────────────────────────────┼─────────────────────────────────┤
│ Folder: frontend/               │ Folder: backend/                │ Folder: eval/ + prompts/        │
│                                 │                                 │                                 │
│ • Intake screen: intent +       │ • API server (FastAPI/Express)  │ • Gemini pipeline: intent       │
│   role selector + PDF opsional  │ • PDF ingest + syllabus store   │   classification, checklist gen │
│ • Realtime checklist UI         │ • Session/chapter state machine │ • Syllabus chunking + PDF-RAG   │
│ • Chapter stepper + gated reader│   LOCKED→ACTIVE_READING→        │ • Google Search grounding       │
│ • Select-word ask popover +     │   INTERVIEW→SCORED→UNLOCKED/    │   (opsional, 1 chapter, cached) │
│   suggested questions           │   NEEDS_REVIEW                  │ • Socratic interviewer prompt   │
│ • Interview quiz UI             │ • Focus-event ingest            │ • Honeypot generator +          │
│ • Focus Mode camera + auto-blur │ • DEMO_MODE=cached fallback     │   4-class classifier            │
│ • Calibration slider + report   │ • Cloud Run deploy + Firestore  │ • Calibration + verifier loop   │
│                                 │                                 │ • eval/ harness + benchmarks    │
├─────────────────────────────────┼─────────────────────────────────┼─────────────────────────────────┤
│ Budget: 3.25 dev-day            │ Budget: 3.10 dev-day            │ Budget: 3.25 dev-day            │
└─────────────────────────────────┴─────────────────────────────────┴─────────────────────────────────┘
```

Aturan batas folder: dev boleh baca folder lain, **hanya owner yang nulis**. Kalau butuh perubahan di folder orang lain → minta di sync, bukan commit sendiri.

---

## 3. Feature Ownership Matrix (fitur → owner → endpoint → artefak)

| # | Fitur (PRD §4) | Owner | Endpoint (API-CONTRACTS §2) | Artefak bukti |
|---|---|---|---|---|
| F1 | Intake: intent + role selector + PDF opsional | DEV 1 | `POST /intake`, `GET /roles` | Screenshot intake, JSON 201 |
| F2 | Realtime checklist (streaming + edit) | DEV 1 (UI) / DEV 3 (prompt) | `POST/PUT /intake/:id/checklist` | Event `checklist.partial` → `checklist.done` |
| F3 | Syllabus synthesis + chapter metadata | DEV 2 (store) / DEV 3 (AI) | `POST /intake/:id/syllabus` | JSON chapter + `source_pages` |
| F4 | PDF-RAG page anchor | DEV 3 | — (internal) | Klaim honeypot bisa diverifikasi ke halaman |
| F5 | Grounding eksternal (1 chapter, cached) | DEV 3 | `enable_search_grounding: true` | `cached: true` di `references[]` |
| F6 | Chapter stepper + gated reader | DEV 1 | `GET /chapters/:id` | `next_locked: true` di layar |
| F7 | Select-word Socratic ask | DEV 1 (popover) / DEV 3 (prompt) | `POST /chapters/:id/ask` | `gave_direct_answer: false` |
| F8 | Suggested questions (multi-kata) | DEV 1 / DEV 3 | `GET /chapters/:id/suggestions` | 3 pertanyaan per seleksi |
| F9 | Interview quiz multi-turn (2-3 ronde) | DEV 1 (UI) / DEV 3 (prompt) | `POST /chapters/:id/interview/{start,turn,finalize}` | `running_score`, `is_concluded` |
| F10 | Honeypot generator + 4-class classifier | DEV 3 | (di dalam `interview/turn`) | `honeypot_verdict.result` + skor ± |
| F11 | Focus Mode (MediaPipe on-device) + auto-blur | DEV 1 (ML/UI) / DEV 2 (ingest) | `POST /chapters/:id/focus-events` | `video_transmitted: false`, flag `assisted` |
| F12 | Accessible Mode (kamera off) | DEV 1 / DEV 2 | idem F11 | `integrity_flag: assisted_unverified` |
| F13 | Single score per chapter + threshold 75 | DEV 3 (hitung) / DEV 2 (state) | `interview/finalize` | `chapter_score` + transisi state |
| F14 | Calibration gap (predict before reveal) | DEV 1 (slider) / DEV 3 (label) | `POST /chapters/:id/calibration` | `calibration_gap` + `label` |
| F15 | Verifier loop + appeal path (stub) | DEV 3 | `interview/finalize`, `POST /chapters/:id/appeal` | `verifier.status` |
| F16 | Final report | DEV 1 (view) / DEV 2 (agregasi) | `GET /report/:sessionId` | JSON report + screenshot |
| F17 | Cached fallback (2 skenario) | DEV 2 | `DEMO_MODE=cached` / header | Banner `LOCAL_DETERMINISTIC_CACHE` |
| F18 | Eval harness + angka | DEV 3 | — (offline) | `eval/results/*.jsonl` + tabel |

**CUT (jangan dikerjakan, masuk roadmap slide):** Monaco + Piston + TDL, DAG Skill Tree (ReactFlow), dual-metric, voice/Gemini Live, auth multi-user, input video/audio. Referensi: [PRD.md](./PRD.md) §8.

---

## 4. Rincian Task Harian (Day-by-Day Sprint)

### Hari 0 — Rabu, 14 Oktober (malam ini: setup & baseline)

**DEV 1 — Frontend**
- Init project Next.js 15 (App Router, TypeScript, Tailwind) di `frontend/`: `npx create-next-app@latest frontend --typescript --tailwind --app`.
- Buat route skeleton: `/intake`, `/checklist`, `/syllabus`, `/chapter/[id]`, `/interview/[id]`, `/report/[sessionId]`.
- Salin **semua contoh JSON dari [API-CONTRACTS.md](./API-CONTRACTS.md) §2** ke `frontend/mocks/*.json` — ini yang dipakai sampai backend siap (No Blocker Rule §6.1).
- Render statis: intake screen (3 input, tanpa tombol "Summarize" di mana pun) + checklist dengan checkbox.

**DEV 2 — Backend**
- Init API server (FastAPI atau Express) di `backend/`, prefix `/api/v1`.
- Implement `POST /api/v1/intake` + `GET /api/v1/roles` (9 role seed + `Others`, lihat [API-CONTRACTS.md](./API-CONTRACTS.md) §2.1).
- Session store in-memory dulu (Firestore besok), plus middleware fallback: header `x-demo-mode: cached` → balas cache lokal.
- Tulis `Dockerfile` backend (jangan deploy malam ini, deploy Hari 1/3).

**DEV 3 — AI Engine**
- Setup koneksi Gemini lewat **Google Gen AI SDK** (`google-genai` / `@google/genai`), env `GOOGLE_API_KEY` / Vertex project.
- Tes `response_schema` (JSON Schema di [API-CONTRACTS.md](./API-CONTRACTS.md) §4) — target: parse tanpa exception.
- Draft prompt Socratic interviewer + katalog honeypot deterministik (ADR 002), **10 term** untuk uji malam ini.
- Buat `eval/` (lihat §6.5): harness pemanggil model + classifier 4 kelas. Rujuk metodologi di [HASIL-TES-EMPIRIS.md](../reza-research/parts10/HASIL-TES-EMPIRIS.md) supaya angka baru bisa dibandingkan dengan baseline (n=80).

**Gate Hari 0:** API-CONTRACTS v2 di-freeze; 3 repo folder (`frontend/`, `backend/`, `eval/`) jalan lokal; mock JSON lengkap; 10 honeypot term tervalidasi ulang.

---

### Hari 1 — Kamis, 15 Oktober (intake → checklist → syllabus)

**DEV 1 — Frontend**
- Intake screen final: intent free-text (min 3 kata, validasi), role selector dari `GET /roles`, opsi `Others` muncul otomatis saat `suggested_others: true`, slot PDF opsional dengan state "no document" yang jelas.
- Checklist UI realtime: konsumsi SSE `checklist.partial` per item → `checklist.done`; tampilkan checkbox, `confidence`, dan tag `origin` (`document` / `role_taxonomy` / `grounded_external`).
- Uncheck/check + `PUT /intake/:id/checklist` → lanjut ke `/syllabus`.

**DEV 2 — Backend**
- `POST /intake/:sessionId/checklist` (varian JSON + `stream: true`), `PUT /intake/:sessionId/checklist`.
- PDF ingest: ekstraksi teks + nomor halaman (page-anchored), simpan ke store.
- `POST /intake/:sessionId/syllabus` — handler + persist syllabus/chapter ke Firestore, balas schema [API-CONTRACTS.md](./API-CONTRACTS.md) §2.3.
- Deploy pertama ke Cloud Run (pastikan URL `*.a.run.app` hidup), Cloud Logging nyala.

**DEV 3 — AI Engine**
- Intent classification + deteksi role tidak match seed → `suggested_others: true` (ADR 004).
- Prompt checklist generation: keluarkan item + `origin` + `confidence`.
- Syllabus chunking: chapter berstruktur (`title`, `order`, `objectives`, `estimated_reading_minutes`, `source_pages`) — bukan chunk 300-600 kata buta.
- PDF-RAG: page anchor per chapter; jalur **tanpa PDF** → `source_mode: role_taxonomy_generated`.
- Grounding eksternal: aktifkan untuk **1 chapter saja**, hasil di-cache ke Firestore (fallback ke cache kalau API error).

**Gate Hari 1:** dari satu layar intake, checklist muncul streaming dan bisa di-edit; submit → ≥ 3 chapter dengan `source_pages`; jalur tanpa PDF tetap menghasilkan chapter bertanda `source_mode`.

---

### Hari 2 — Jumat, 16 Oktober (chapter reader + interview + honeypot)

**DEV 1 — Frontend**
- **Chapter stepper linear** (bukan DAG): nomor, judul, badge status dari state machine.
- Gated reader: konten chapter, panel referensi (`document` page anchor + `grounded_external` dengan `cached: true`), tombol `Next` disabled selama `next_locked: true`.
- Select-word popover: panggil `POST /chapters/:id/ask`, tampilkan balasan Socratic + `hint_level` + `citations`, dan **tampilkan `gave_direct_answer: false`** di panel response (ini bukti tesis, jangan disembunyikan).
- Multi-kata terpilih → `GET /chapters/:id/suggestions` → 3 pertanyaan yang bisa diklik.
- Interview UI: multi-turn, timer tekanan respons (mulai setelah pertanyaan selesai di-stream), banner verdict honeypot.

**DEV 2 — Backend**
- `GET /chapters/:chapterId` + state machine penuh: `LOCKED → ACTIVE_READING → INTERVIEW → SCORED → UNLOCKED/NEEDS_REVIEW` ([API-CONTRACTS.md](./API-CONTRACTS.md) §1). Honeypot **tidak** mengubah state, hanya mengisi `honeypot_score`.
- `POST /chapters/:id/interview/{start,turn,finalize}`; simpan riwayat turn; teruskan `client_telemetry` (`paste_detected`, `duration_seconds`, `keystroke_cpm`).
- Threshold unlock ≥ 75, `< 75` → `NEEDS_REVIEW` (retry), bukan dead-end.
- Endpoint `/report/:sessionId` (agregasi dasar) supaya DEV 1 bisa wiring lebih awal.

**DEV 3 — AI Engine**
- Socratic interviewer prompt: 2-3 ronde, pertanyaan inferensial/HOTS + adaptive follow-up (bukan "apa definisi X").
- Honeypot generator: katalog deterministik + variasi term (ADR 002 + ADR 005) supaya tidak dihafal.
- 4-class classifier → skor: `CRITICAL_REJECTION` +2, `AI_HALLUCINATION_COPYPASTE` −2, `UNVERIFIED_HONEST` 0, `EVASIVE` −1.
- Verifier loop: model kedua (Gemini Pro) meninjau skor; `verifier.status` = `agreed` / `uncertain`.

**Gate Hari 2:** chapter 2 tetap `LOCKED` sampai skor chapter 1 ≥ 75; jalur copas jawaban LLM luar → `AI_HALLUCINATION_COPYPASTE` (−2); jalur tolak premis → `CRITICAL_REJECTION` (+2). Keduanya harus terlihat di UI, bukan cuma di JSON.

---

### Hari 3 — Sabtu, 17 Oktober (Focus Mode + scoring + calibration + fallback)

**DEV 1 — Frontend**
- Focus Mode: kamera nyala, MediaPipe on-device (head-pose/gaze drift, jumlah wajah > 1, tab blur). Terdeteksi → **auto-blur halaman** + badge `assisted`.
- Accessible Mode: satu toggle (kamera off, blur off, waktu longgar) → status `assisted_unverified`.
- Calibration slider: user prediksi skor (0-100) **sebelum** reveal → tampilkan `predicted_score`, `actual_score`, `calibration_gap`, `label` (`overconfident` / `underconfident` / `well_calibrated`).
- Report view: skor per chapter, mean calibration gap, integrity flags, honeypot verdict log, tombol appeal (stub).

**DEV 2 — Backend**
- `POST /chapters/:id/focus-events`: terima **event boolean saja**, `video_transmitted` wajib `false` (ADR 003), balas `integrity_flag` + `auto_blur` + `summary`.
- `DEMO_MODE=cached` (+ header `x-demo-mode: cached`): 2 skenario pre-cached — success flow (`CRITICAL_REJECTION`, skor tinggi, unlock) dan caught flow (`AI_HALLUCINATION_COPYPASTE`, skor turun, flag integrity). Cache juga menyimpan hasil grounding.
- Fallback otomatis saat Gemini error `429/500/503`, balas `{ fallback_active: true, source: "LOCAL_DETERMINISTIC_CACHE" }` tanpa exception.
- Deploy Cloud Run final + verifikasi URL publik dari jaringan luar (HP, bukan cuma localhost).

**DEV 3 — AI Engine**
- Skoring deterministik dari klasifikasi LLM (ADR 002): single `chapter_score` 0-100 + `reasoning_score` + `integrity_score` + `honeypot_score`. **Bukan** dua metrik paralel.
- Calibration label + appeal handler (verifier sebagai reviewer, outcome `upheld` / `revised` / `uncertain`).
- **Eval harness final** di `eval/`: jalankan suite → simpan `eval/results/*.jsonl` + tabel ringkas (honeypot hallucination rate, trap effectiveness per jenis, sycophancy gap, verifier catch rate, valid-JSON rate).
- Semua angka untuk deck/README diambil **hanya** dari `eval/results/` atau [HASIL-TES-EMPIRIS.md](../reza-research/parts10/HASIL-TES-EMPIRIS.md).

**Gate Hari 3:** alur penuh intake → report jalan dua kali berturut-turut: sekali online, sekali `DEMO_MODE=cached`. Nol spinner kosong. Angka eval tersimpan di file.

---

### Hari 4 — Minggu, 18 Oktober (deploy + video + deck + submit)

| Waktu (UTC+7) | Kegiatan | Owner | Output |
|---|---|---|---|
| 09:00 – 11:00 | Deploy final + smoke test 2 skenario cached dari HP | DEV 2 | URL Cloud Run live, log bersih |
| 11:00 – 13:00 | Gladi resik + rekam video 3 menit (1080p, EN, cached) | DEV 1 | File video siap upload |
| 13:00 – 16:00 | Deck PDF 10 slide EN (dari [PITCH-DECK-OUTLINE.md](./PITCH-DECK-OUTLINE.md)) + README repo + diagram arsitektur | DEV 1 + DEV 3 | `deck.pdf`, `README.md` |
| 16:00 – 18:00 | Audit git (tidak ada `.env`/token), upload YouTube, rapikan URL | DEV 2 | Repo publik bersih |
| 18:00 – 19:30 | Submit portal Hack2skill: video + deck PDF + URL Cloud Run + URL GitHub | Semua | Konfirmasi submit |
| **sebelum 20:00** | **SUBMIT DONE** — buffer 4 jam sebelum 23:59 UTC+8 | — | — |
| 20:00 – 23:59 | Buffer. **Freeze kode.** Kalau ada bug, perbaiki di video/deck, bukan di repo | — | — |

**Gate Hari 4:** submission terkirim sebelum 20:00 UTC+8; repo publik tanpa secret; video 180 detik; deck 10 slide bahasa Inggris (PRD §7: UI, README, deck, video = Inggris).

---

## 5. Checkpoint & Definition of Done

**Sync wajib (No Blocker Rule §6.3): 12:00 dan 21:00, 15 menit, agenda tetap:**

1. Blocker yang saya punya → siapa yang buka jalannya.
2. Kontrak yang saya butuh ubah (kalau ada).
3. Apa yang jalan **sekarang** (demo 30 detik, bukan deskripsi).

**EOD freeze, tiap hari 23:00 (UTC+7):**

| Hari | Yang harus hijau di EOD | Kalau merah |
|---|---|---|
| 0 | 3 folder jalan, mock JSON lengkap, 10 honeypot term tervalidasi | Pakai mock, lanjut Hari 1 |
| 1 | intake → checklist → syllabus (dengan & tanpa PDF) | Frontend lanjut dari mock; DEV 3 potong grounding |
| 2 | gate locked/unlock + 2 verdict honeypot terlihat di UI | Interview jadi 2 ronde tetap, follow-up adaptif dibuang |
| 3 | alur penuh online **dan** cached, angka eval tersimpan | Eksekusi §7 cut cadangan, jangan lembur fitur baru |
| 4 | submission terkirim | Prioritas: video + deck + URL live. Fitur terakhir dikorbankan |

**Aturan rollback:** fitur yang tidak jalan di EOD di-rollback ke mock/cached. Tidak ada fitur setengah jalan yang dibawa ke hari berikutnya — itu yang bikin demo mati di depan juri.

---

## 6. Komitmen Saling Mengunci (No Blocker Rule)

### 6.1 Frontend tidak menunggu backend — pakai mock
Frontend **wajib** bisa jalan penuh dari `frontend/mocks/*.json` yang disalin dari contoh JSON di [API-CONTRACTS.md](./API-CONTRACTS.md). Kalau endpoint belum ada, frontend ganti base URL ke mock adapter — bukan berhenti. Backend mengejar schema, bukan sebaliknya.

### 6.2 Google AI SDK only
Semua kode produk hanya pakai **Google AI SDK** (Gemini via Vertex AI / Google Gen AI SDK). Dilarang meng-install `openai`, `anthropic`, atau `cohere` di `package.json` / `requirements.txt` produk — pelanggaran aturan event = risiko nol di Technical Merit 40% (PRD §7).

Pengecualian sempit: harness di `eval/` boleh memanggil model non-Google **lewat HTTP gateway** untuk mengukur efektivitas trap (metodologi riset di [HASIL-TES-EMPIRIS.md](../reza-research/parts10/HASIL-TES-EMPIRIS.md)). Syaratnya: tidak boleh jadi dependency runtime produk, tidak diimpor oleh `backend/`, dan tidak disebut sebagai bagian arsitektur Assay di deck.

### 6.3 Sync harian
Sync 15 menit setiap **12:00 dan 21:00** (UTC+7). Blocker yang menggantung > 2 jam wajib diangkat ke channel, bukan dipendam. Blocker tanpa solusi = turun ke fallback cached, lanjut kerja.

### 6.4 Kontrak beku
Setelah Hari 0, perubahan [API-CONTRACTS.md](./API-CONTRACTS.md) hanya lewat kesepakatan bertiga dan harus langsung di-reflect ke `frontend/mocks/`. Endpoint/field yang berubah tanpa update mock = blocker semua orang.

### 6.5 Angka hanya dari sumber yang bisa diaudit
Semua angka di deck, README, dan video harus bisa ditelusuri ke `eval/results/` atau [HASIL-TES-EMPIRIS.md](../reza-research/parts10/HASIL-TES-EMPIRIS.md). Dilarang mengarang angka (PRD §9 — deck v1 pernah menulis "91.3% / 640ms" tanpa sumber; jangan diulang).

### 6.6 Batas folder
`frontend/` milik DEV 1, `backend/` milik DEV 2, `eval/` + `prompts/` milik DEV 3. Cross-folder butuh izin owner di sync.

---

## 7. Urutan Cut Cadangan (kalau Hari 3 masih merah)

Eksekusi dari atas, satu per satu, sampai beban masuk kapasitas. Jangan improvisasi urutan.

| # | Cut | Dampak ke demo |
|---|---|---|
| 1 | Appeal path → stub (tampilkan `under_review`, tanpa model kedua) | Kecil — appeal bukan momen demo |
| 2 | Google Search grounding → matikan total, PDF-RAG saja | Kecil — grounding cuma pelengkap |
| 3 | Interview multi-turn → 2 ronde tetap, adaptive follow-up dibuang | Sedang — jawaban Q&A juri sudah disiapkan di [AUDIT.md](./AUDIT.md) §10 |
| 4 | Focus Mode → 1 event (`MULTIPLE_FACES`) + tab blur | Sedang — jual sebagai "integrity signal", jangan klaim anti-cheat |
| 5 | Report trend chart → tabel angka | Kecil |
| — | **Tidak boleh di-cut:** honeypot, gate unlock ≥ 75, calibration gap, cached fallback, eval harness + angka | — |

---

## 8. Risiko Sprint & Trigger Aksi

| # | Risiko | Trigger yang bisa dilihat | Aksi |
|---|---|---|---|
| R1 | Scope kebesaran (14.75 vs 9.6 dev-day) | EOD Hari 2 merah | Jalankan §7, bukan lembur |
| R2 | Honeypot gagal (LLM luar menolak halusinasi) | Rate uji ulang < 40% | Pakai term cadangan jenis `fictional_term` yang sudah terbukti di [HASIL-TES-EMPIRIS.md](../reza-research/parts10/HASIL-TES-EMPIRIS.md) P2 |
| R3 | Penilaian LLM terasa subjektif | Juri menanyakan konsistensi skor | Tunjukkan ADR 002 + `verifier.status` + appeal path |
| R4 | Gemini down / rate limit saat demo | Error 429/500/503 | `DEMO_MODE=cached` 2 skenario; jangan rekam tanpa cached |
| R5 | "Anti-cheat" dibongkar juri | Pertanyaan "bisa di-bypass?" | Jangan klaim anti-cheat. Jual "Focus Mode / integrity signal" + Accessible Mode (Q&A di [AUDIT.md](./AUDIT.md) §10) |
| R6 | MediaPipe gagal load di device rekaman | Kamera/model tidak init di Hari 3 pagi | Fallback: tab-blur + `CAMERA_OFF` event, tetap tampilkan panel Focus Mode |
| R7 | Data honeypot di-cache basi | Skenario cached tidak match UI terbaru | Regenerate cache setiap kali schema berubah (DEV 2, Hari 3) |

---

## 9. Artefak Submisi (Checklist Hari 4)

- [ ] URL Cloud Run live (`*.a.run.app`), diuji dari jaringan luar
- [ ] URL GitHub publik, tanpa `.env` / token / key
- [ ] Video demo 3 menit, 1080p, voiceover Inggris, tanpa musik latar
- [ ] Deck PDF 10 slide bahasa Inggris
- [ ] README repo: cara jalan, arsitektur, cara aktifkan `DEMO_MODE=cached`
- [ ] Tabel angka eval dari `eval/results/`
- [ ] Submission terkirim di portal Hack2skill **sebelum 20:00 UTC+8 (18 Okt 2026)**

---

## 10. Angka yang Boleh Dipakai (dan satu yang harus diverifikasi)

Sumber: [HASIL-TES-EMPIRIS.md](../reza-research/parts10/HASIL-TES-EMPIRIS.md) — jangan dibulatkan naik, jangan ditambah.

| Klaim | Angka | Sampel | Status |
|---|---|---|---|
| Honeypot hallucination rate (semua model) | 54% | n = 80 panggilan, 4 model | Aman |
| — gemini-flash-medium / deepseek-v4-pro / deepseek-v4-flash / deepseek-v4.1-flash | 75% / 70% / 45% / 25% | 20 panggilan masing-masing | Aman |
| Trap effectiveness: `trap_number` | 58% | n = 48 | Aman |
| Trap effectiveness: `false_premise` / `over_claim` | 25% / 25% | n = 48 | Aman |
| Verifier loop menangkap halusinasi | 13/20 (65%) | 20 jawaban halusinasi | Aman |
| Structured output JSON valid | 4/4 (100%) | 4 panggilan schema | Aman |
| Trap effectiveness: `fictional_term` | **100%** (10 comply / 0 pushback / 2 error) — **RESOLVED**: 67% di PRD §9 lama salah (ERROR dihitung sebagai PUSHBACK) | n = 12 valid | Aman. Pakai 100% + sebut n=12 |
| Latency | 26s rata-rata lintas model | — | **Jangan dipakai di video** (tidak demo-relevan) |
| Angka apa pun yang tidak ada di tabel ini | — | — | Dilarang muncul di submisi |

---

**Penutup:** kapasitasnya 9.6 dev-day, bebannya 14.75. Rencana ini sudah memotong 5.15 dev-day untuk menutup selisih itu. Kalau ada yang nambah fitur di luar tabel §3, itu bukan kerja ekstra — itu utang yang dibayar di Hari 4 dengan video yang gagal rekam.
