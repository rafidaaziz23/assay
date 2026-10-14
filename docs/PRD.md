# Product Requirements Document (PRD) — v2.0.0
## Assay: The Active Socratic Learning Engine
*(codename repo: Active Learning Engine — `active-learning-engine/`)*

**Event:** AI Builder Cup 2026 (Google Cloud x Hack2skill, JAPAC)
**Target Submission Deadline:** 18 Oktober 2026, 23:59 UTC+8 — **HARD DEADLINE**
**Track Alignment:** Track 4 (Media, Content & Digital Experiences — Adaptive Learning) — **single track**
**Author / Core Team:** AI Builder Cup Squad (3 developer)
**Document Version:** 2.0.0
**Status:** OPERATIONAL CONTRACT — mengikat. Dokumen ini menggantikan PRD v1.0.0.

---

## 0. Changelog v1.0.0 → v2.0.0

Ringkas apa yang berubah, biar gak ada yang bingung baca dua versi.

| Area | v1.0.0 | v2.0.0 | Alasan |
|---|---|---|---|
| Nama produk | CogniForge | **Assay** | "Cogni-" pola AI-slop; "Assay" = uji kemurnian logam + homofon "essay" |
| Entry point | Upload PDF (wajib) | Intent input + Role selector + PDF (**opsional**) | Flow baru: user mulai dari niat belajar, bukan dari dokumen |
| Track | Track 4 **dan** Track 5 | Track 4 saja | Rules: 1 tim = 1 track |
| Deadline | 19 Oktober | **18 Oktober** | Deadline resmi panitia |
| Tim | 4 developer | **3 developer** | Realita squad |
| Kurikulum | Chunk 300-600 kata → concept node | Intent+role → checklist → **silabus chapter** | Flow baru |
| Skor | Dual-metric (Concept + Reasoning) | **Single score + Calibration Gap** | Lebih murah, lebih kuat demo (riset C1) |
| Honeypot | Gate keras (kena = fail) | **Dimensi skor** (+2/-2/0/-1), bukan gate | Riset A1: gate keras ngehukum orang jujur |
| Visual tree | DAG Skill Tree (ReactFlow) | **Chapter stepper linear** | DAG gak pembeda, buang 1 dev-day |
| Coding arena | Monaco + Piston + TDL | **CUT ke roadmap** | Gak muat 4 hari |
| Anti-cheat | CSS `user-select:none` + blur + timer | **Focus Mode (MediaPipe ML, on-device) + auto-blur** | Riset B1/B2: jangan jual "anti-cheat", aksesibilitas |
| Select-word | (tidak ada) | **Select kata → tanya AI (Socratic)** + suggested question | Fitur baru flow |
| Referensi | (tidak ada) | **PDF-RAG wajib + Google Search grounding opsional** | Fitur baru flow |
| Nama file | `docs/adrs/001-model-selection.md` | ADR 001-005 (lihat §11) | Tambah ADR keputusan baru |

---

## 1. Executive Summary & Value Proposition

### 1.1 The "Anti-AI-Brain-Rot" Manifesto
Di era Generative AI, platform belajar konvensional dan dokumen materi (PDF/modul) mengalami krisis efektivitas: **AI Brain Rot**. Pelajar dan engineer memasukkan materi ke ChatGPT atau NotebookLM untuk minta ringkasan instan, kuis instan, atau jawaban kode — tanpa proses penalaran. Akibatnya:
- Otot kognitif melemah (*atrophy of critical thinking*).
- Retensi jangka panjang anjlok.
- Pemahaman palsu (*illusory competence*): merasa paham karena baca rangkuman AI, tapi runtuh saat hadapi *edge case* nyata.

**Bukti angka (dari riset primer, dipakai di deck):**
- 95% mahasiswa pakai AI (HEPI 2026).
- 67% murid bilang AI merusak cara berpikir mereka (RAND, Mar 2026).
- PISA 2025 terendah sepanjang sejarah (OECD, Sep 2026).
- 72% employer susah mengisi posisi (ManpowerGroup 2026).
- Unguarded AI helper = 17% **lebih buruk** hasilnya; AI yang menolak menjawab = kerusakan hilang (arXiv 2606.26181, Jun 2026).

### 1.2 Solusi: Assay
**Assay** membalik paradigma AI dari **"Passive Answer Dispenser"** menjadi **"Active Socratic Enforcer & Interrogator"** dengan filosofi **High-Friction, High-Reward**.

Assay gak ngasih ringkasan gratis. Sistem:
1. Ambil **niat belajar** user + **role** yang mau dikuasai + (opsional) **dokumen pendukung**.
2. Generate **checklist topik** realtime sesuai niat + isi dokumen.
3. Susun **silabus ber-chapter** dari dokumen, diperkaya **referensi eksternal** yang relevan.
4. Kunci chapter berikutnya sampai user lulus **interview quiz**.
5. Di dalam chapter, user bisa **select kata** buat nanya balik ke AI — dan AI-nya **balik nanya** (Socratic), bukan ngasih jawaban.
6. Selipkan **honeypot** (konsep fiktif) buat nangkep user yang copas ke LLM luar.
7. **Focus Mode** pakai kamera + ML on-device buat deteksi kecurangan → auto-blur.
8. Akhiri dengan **skor per chapter + calibration gap** (jarak antara "ngerasa paham" dan "beneran paham").

```
+--------------------------------------------------------------------------------+
|                    USER INTAKE (single screen)                                  |
|  "What do you want to learn today?"  +  Role selector  +  PDF (optional)       |
+--------------------------------------------------------------------------------+
                                    |
                                    v
+--------------------------------------------------------------------------------+
|                    REALTIME CHECKLIST GENERATION                                |
|  Backend kirim checklist topik (role-based) sesuai niat + isi PDF              |
+--------------------------------------------------------------------------------+
                                    |
                                    v
+--------------------------------------------------------------------------------+
|                    SYLLABUS SYNTHESIS                                           |
|  AI chunk PDF -> chapters  +  ambil referensi relevan (PDF-RAG + grounding)     |
+--------------------------------------------------------------------------------+
                                    |
                                    v
+--------------------------------------------------------------------------------+
|                    GATED CHAPTER READER                                         |
|  Chapter linear, next LOCKED sampai interview quiz lulus                        |
|  Di dalam chapter: select kata -> tanya AI (Socratic) + suggested questions     |
+--------------------------------------------------------------------------------+
                                    |
                                    v
+--------------------------------------------------------------------------------+
|                    INTERVIEW QUIZ (per chapter)                                 |
|  - Honeypot (konsep fiktif)                                                     |
|  - Focus Mode: kamera + ML on-device, anti-cheat, auto-blur kalau curang        |
|  - Calibration: user prediksi skor sendiri sebelum reveal                       |
+--------------------------------------------------------------------------------+
                                    |
                                    v
+--------------------------------------------------------------------------------+
|                    SCORING & REPORT                                             |
|  Single score per chapter + Calibration Gap + integrity flags                   |
+--------------------------------------------------------------------------------+
```

### 1.3 Positioning (satu kalimat, pakai di deck slide 1)
> Setiap AI study tool menjawab pertanyaan. Assay yang mempertanyakan jawabanmu.

---

## 2. Problem Statement & Competitive Positioning

### 2.1 Landscape
| Karakteristik | NotebookLM / ChatGPT / Coursera | **Assay** |
|---|---|---|
| Peran AI | Perpustakaan & asisten pasif | Pelatih & penguji penalaran |
| Ringkasan | 1-klik instan | **Gak ada tombol ringkasan**. User yang nulis |
| Alur materi | Linear pasif / bebas lompat | **Chapter terkunci** sampai lulus interview |
| Integritas | Gak ada verifikasi | **Honeypot + Focus Mode ML** |
| Interaksi dalam materi | Gak ada / chat terpisah | **Select kata → tanya AI (Socratic)** |
| Metrik | Skor pilihan ganda | **Skor reasoning + calibration gap** |

### 2.2 Kompetitor terdekat & diferensiasi
- **Khanmigo / Google Learn About:** Socratic tapi *suggestive* — user bisa minta jawaban langsung, gak ada gatekeeping, gak ada deteksi integritas, gak bisa upload PDF sendiri. Assay = *enforcement engine*, bukan tutor sugestif.
- **Foreman (kompetitor Track 5, AI Builder Cup 2026):** "Honesty Canary" buat uji kejujuran **agen AI**. Assay punya DNA mekanisme yang sama, tapi menguji **kejujuran manusia yang nyontek AI lain**. Posisi filosofis yang kuat — sebut di deck.
- **Chopdesk (Track 1):** punya heuristic offline fallback. Assay wajib punya kelas fallback yang sama.

### 2.3 Persona & pasar
- **Demo (B2C, human-facing):** pelajar/developer yang mau naik level dari role tertentu (Frontend/Backend/Fullstack/dll).
- **Story & monetisasi (B2B, institution-facing):** bootcamp & corporate L&D yang gak bisa lagi percaya nilai/sertifikat/portofolio karena AI. Assay = sistem verifikasi reasoning.
- **Relevansi JAPAC:** gap 9 juta talenta digital (World Bank); bootcamp dengan completion rate <15% dan kompetensi gak terverifikasi.

---

## 3. Core User Flow (KANONIK)

Ini flow resmi. Semua dokumen lain (API-CONTRACTS, DEMO-SCRIPT, PITCH-DECK, TEAM-TASK) harus mengikuti urutan ini.

### Step 1 — Intake Screen
Satu layar berisi tiga input:
1. **Intent:** free-text — *"What do you want to learn today?"*
2. **Role selector:** daftar **role fix** (seed) yang bisa dipilih, e.g. `Frontend`, `Backend`, `Fullstack`, `DevOps`, `Data/ML`, `Mobile`, `QA/Test`, `Security`, `System Design`. Kalau niat user gak ada di seed → backend otomatis memunculkan opsi **`Others`** (free-text role).
3. **PDF upload (opsional):** dokumen pendukung. Boleh kosong.

### Step 2 — Realtime Checklist Generation
Setelah submit, backend generate **checklist topik** secara realtime berdasarkan: (a) intent, (b) role terpilih, (c) isi PDF (kalau ada). Frontend menampilkan checklist dengan checkbox; user boleh uncheck/check item sebelum lanjut. Item yang dicentang = bahan silabus.

### Step 3 — Syllabus Synthesis
Backend integrasi AI:
- **Chunking:** pecah PDF jadi beberapa **chapter silabus** berstruktur (judul, urutan, tujuan, estimasi waktu).
- **Reference enrichment:** AI mengambil **referensi relevan** dari sumber tambahan buat memperkuat hasil pembelajaran.
  - **PDF-RAG (wajib):** grounding di dalam dokumen, page-anchored. Ini yang bikin klaim honeypot bisa diverifikasi.
  - **Google Search grounding (opsional):** diaktifkan cuma untuk 1-2 chapter, hasilnya **di-cache**, fallback ke cache kalau API error.
- Kalau **tidak ada PDF:** konten chapter di-generate AI dari role taxonomy + grounding (chapter tetap jalan), ditandai sumbernya.

### Step 4 — Gated Chapter Reader
- Frontend menampilkan tiap **chapter silabus**.
- **Guard:** chapter berikutnya **terkunci** sampai user lulus interview quiz chapter saat ini.
- Di dalam halaman chapter, user bisa **select kata/kalimat** dari konten → muncul popover buat **tanya AI**.
  - AI menjawab **secara Socratic** (balik nanya / kasih hint), **bukan** ngasih jawaban langsung.
  - Kalau user select **beberapa kata**, AI menampilkan **suggested questions** yang relevan dengan seleksi itu.

### Step 5 — Interview Quiz (per chapter)
Setiap chapter punya **interview quiz** dengan:
- **Honeypot:** AI menyelipkan konsep fiktif yang meyakinkan. Klasifikasi respons → dimensi skor (bukan gate).
- **Focus Mode (kamera):** kamera nyala + **ML on-device** (MediaPipe) mendeteksi indikasi kecurangan (gaze/head-pose drift, jumlah wajah >1, pindah tab). Kalau terdeteksi → **halaman auto-blur** + event di-flag `assisted`.
  - **Privasi:** inferensi jalan di browser; **video TIDAK dikirim ke server**, cuma event boolean.
- **Anti-cheat feature** (dijual sebagai *focus & integrity signal*, bukan klaim "gak bisa dicurangi").
- **Calibration:** sebelum skor di-reveal, user memprediksi skor dirinya sendiri (0-100).

### Step 6 — Scoring & Final Report
- **Single score per chapter** (0-100), threshold unlock **≥ 75**.
- **Calibration gap** = |prediksi user − skor aktual|. Dipakai di laporan, **bukan** penentu unlock.
- **Integrity flags** dari Focus Mode + honeypot masuk laporan.
- **Final report:** skor lintas chapter + tren calibration gap + integrity log.

---

## 4. Feature Architecture & Functional Specifications

### 4.1 Pilar 1 — Intake & Role Selector
- **Intent input:** free-text, wajib. Min 3 kata.
- **Role selector:** seed fix (lihat §3 Step 1). Kalau intent gak match seed mana pun → opsi `Others` muncul otomatis (backend deteksi via AI classify). User bisa isi role custom.
- **PDF optional:** PDF/raw text. Kalau ada, jadi sumber konten utama.

### 4.2 Pilar 2 — Realtime Checklist Generation
- Backend generate checklist topik dari (intent + role + isi PDF).
- Frontend render realtime (SSE atau polling cepat).
- User bisa edit pilihan (check/uncheck) sebelum submit.
- Item terpilih → jadi basis chapter silabus.

### 4.3 Pilar 3 — Syllabus Synthesis & Reference Enrichment
- **Chunking by structure:** Gemini pecah dokumen jadi chapter berstruktur (bukan chunk 300-600 kata buta).
- **PDF-RAG:** tiap chapter punya page-anchor ke dokumen. Dipakai buat: (a) konten chapter, (b) verifikasi klaim honeypot ("istilah ini gak ada di halaman mana pun modul lu").
- **Grounding opsional:** Google Search grounding (Vertex AI) buat 1-2 chapter. Hasil di-cache ke Firestore.
- **No-PDF path:** chapter di-generate dari role taxonomy + grounding, ditandai `source: generated`.

### 4.4 Pilar 4 — Gated Chapter Reader & Inline Socratic Ask
- **Chapter stepper linear** (bukan DAG visual). State per chapter: `LOCKED → ACTIVE_READING → INTERVIEW → SCORED → UNLOCKED/NEEDS_REVIEW`.
- **Guard:** `next` terkunci default; unlock hanya setelah skor chapter ≥ 75.
- **Select-word ask:** user select teks di chapter → popover.
  - Mode **Socratic**: AI balik nanya / kasih hint / nunjuk ke halaman relevan. **Tidak** memberi jawaban jadi.
  - Multi-kata terpilih → AI kasih **suggested questions**.
  - Tiap interaksi tercatat (buat metrik engagement + audit).

### 4.5 Pilar 5 — Interview Quiz, Honeypot & Focus Mode
- **Interview multi-turn (2-3 ronde):** pertanyaan inferensial/HOTS, adaptive follow-up. Bukan "apa definisi X".
- **Honeypot:**
  - Konsep fiktif kontekstual (contoh: *"React Quantum Hook"*, *"Zero-Latency Mutex"*, *"bcSQL indexing"*).
  - Dimensi skor honeypot (riset A1):
    - `CRITICAL_REJECTION` (curiga & tepat) → **+2**
    - `AI_HALLUCINATION_COPYPASTE` (panjang, yakin, halusinasi) → **−2**
    - `UNVERIFIED_HONEST` ("gw gak tau") → **0** (jujur, netral)
    - `EVASIVE` (diam/muter gak nyerempet) → **−1**
  - **Bukan gate.** Yang mutusin unlock tetap skor gabungan.
  - Katalog deterministik (ADR 002) + variasi term biar gak dihafal (ADR 005).
- **Focus Mode (kamera):**
  - MediaPipe on-device: head-pose/gaze drift, jumlah wajah, tab blur.
  - Terdeteksi → **auto-blur** halaman + flag `assisted`.
  - Video **tidak** keluar device; hanya event boolean ke backend.
  - **Accessible Mode:** bisa dimatikan (copy boleh, blur off, waktu longgar) — skornya ditandai `assisted`.
- **Response pressure timer:** ngukur **waktu mikir user** (mulai setelah pertanyaan selesai di-stream), bukan waktu tunggu model. Timer = sinyal, bukan auto-fail (riset B3).

### 4.6 Pilar 6 — Scoring, Calibration & Report
- **Single score** per chapter 0-100 (concept + reasoning digabung, dihitung deterministik dari klasifikasi LLM — lihat ADR 002).
- **Threshold unlock:** ≥ 75.
- **Calibration:** user prediksi skor → reveal → `calibration_gap = |predicted − actual|`.
- **Report:** skor per chapter, tren calibration gap, integrity log, honeypot verdict.
- **Appeal path:** user bisa bantah skor; sistem review (verifier model kedua) → tandai `uncertain` atau revisi.

---

## 5. Alokasi Tim (3 Developer)

Kapasitas: 3 orang × 4 hari ≈ 12 dev-day, efektif ~9.6 dev-day (overhead integrasi ~20%).
Total flow baru ≈ 11.25 dev-day + fitur wajib riset ≈ 3.5 dev-day = **~14.75 dev-day**.
**Artinya pemotongan itu WAJIB**, bukan pilihan. Lihat §8.

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

## 6. Timeline Menuju 18 Oktober (HARD DEADLINE)

Hari ini 14 Okt. Sisa 4 hari kerja + buffer.

| Tanggal | Target | Output Kunci |
|---|---|---|
| **14 Okt (Hari 0)** | Kontrak API + honeypot test | PRD v2 + API-CONTRACTS v2 disepakati; angka honeypot empiris (sudah ada: 54%, n=80) |
| **15 Okt (Hari 1)** | Intake → checklist → syllabus | Endpoint intake/checklist/syllabus jalan; PDF chunking + PDF-RAG |
| **16 Okt (Hari 2)** | Reader + interview + honeypot | Chapter reader + guard; interview multi-turn + honeypot klasifikasi |
| **17 Okt (Hari 3)** | Focus Mode + scoring + fallback | MediaPipe + auto-blur; calibration; final report; cached fallback |
| **18 Okt (Hari 4)** | Deploy + video + deck + submit | Cloud Run live; video 3 menit; deck PDF; **submit sebelum 20:00 UTC+8** |

---

## 7. Technical Specifications

- **Stack:** Next.js 15 (App Router, TS, Tailwind) + FastAPI/Express; Gemini via Vertex AI / Google Gen AI SDK; Firestore (state + vector search).
- **Hard requirement event:** model Google saja (Gemini/Gemma); dilarang `openai`/`anthropic`/`cohere` di `package.json`. Deploy di Cloud Run/Firebase.
- **Structured output:** semua penilaian pakai JSON schema + function calling (ADR 002).
- **Model routing:** Gemini Flash = gate/chunking/honeypot/follow-up cepat; Gemini Pro = evaluasi reasoning akhir + verifier (async).
- **Bahasa submisi:** UI, README, deck, video **Inggris**. Dokumen internal boleh Indonesia.
- **Data contracts:** lihat `API-CONTRACTS.md` (v2.0.0) — sumber tunggal untuk endpoint & schema.

---

## 8. Non-Goals (CUT dari MVP) & Roadmap

| Dibuang | Alasan | Nasib |
|---|---|---|
| Monaco + Piston + TDL (coding arena) | Gak muat 4 hari; bukan wedge | Roadmap slide |
| DAG Skill Tree visual (ReactFlow) | Gak pembeda; chapter stepper gratis | Roadmap slide |
| Dual-metric (2 skor) | Single + calibration gap lebih murah & kuat | Digantikan |
| Voice / Gemini Live | Latency + biaya berisiko di live | Roadmap |
| Auth kompleks / multi-user | 1 user demo cukup | Roadmap |
| Multi-source input (video/audio) | PDF cukup buat demo | Roadmap |

**WAJIB ada walaupun 4 hari** (ini yang naikin Technical Merit 40%): eval harness + angka, verifier loop, calibration, cached fallback.

---

## 9. Winning Playbook (Mapping ke Rubrik)

| Rubrik | Bobot | Yang nangkep |
|---|---|---|
| Technical Merit & Gen AI | 40% | Eval harness + angka, verifier loop, model routing, structured output, MediaPipe (Google stack), Cloud Run. **Bukan UI.** |
| Problem Alignment & Impact | 25% | Angka §1.1 (HEPI, RAND, PISA, Manpower) + story B2B |
| Innovation & Creativity | 25% | Honeypot pedagogis + calibration gap + select-word Socratic |
| UX & Solution Design | 10% | Accessible Mode + momen calibration slider + desain bersih |

**Angka bukti (dari `reza-research/parts10/HASIL-TES-EMPIRIS.md`, JANGAN dikarang):**
- Honeypot hallucination rate: **54%** (n=80 panggilan, 4 model). Per model: gemini-flash-medium 75%, deepseek-v4-pro 70%, deepseek-v4-flash 45%, deepseek-v4.1-flash 25%.
- Trap efektivitas: **fictional_term 100%** (10 comply / 0 pushback / 2 error, n=12 valid), trap_number 58%, false_premise 25%, over_claim 25% (n=48).
- Verifier loop: 13/20 halusinasi tertangkap (65%).
- Structured output valid JSON: 4/4 (100%).

> [!WARNING]
> **JANGAN pakai angka karangan.** Deck v1 sempat menulis "91.3% / 640ms" dan demo script "sub-1.2s P95" — angka itu gak punya sumber. Semua angka di submisi harus bisa ditelusuri ke `eval/` atau `HASIL-TES-EMPIRIS.md`.

---

## 10. Risks & Mitigations

| # | Risiko | Level | Mitigasi |
|---|---|---|---|
| R1 | Scope kebesaran (14.75 dev-day vs 9.6 kapasitas) | 🔴 CRITICAL | Cut §8; buffer di Hari 4; jangan nambah fitur |
| R2 | Honeypot gagal (LLM luar nolak halusinasi) | 🟠 HIGH | Pakai angka empiris; pin model paling mudah terpancing + term `fictional_term` (terkuat, 100% di n=12) |
| R3 | LLM nilai LLM = subjektif | 🟠 HIGH | Deterministic classification (ADR 002) + verifier loop + appeal |
| R4 | Gemini down / rate limit saat demo | 🟠 HIGH | `DEMO_MODE=cached` (2 skenario: sukses + copas-tertangkap) |
| R5 | "Anti-cheat" dibongkar juri | 🟠 HIGH | Jangan klaim anti-cheat; jual "Focus Mode / integrity signal"; jujur no system is cheat-proof |
| R6 | Aksesibilitas (blur/copy-block) | 🟡 MEDIUM | Accessible Mode toggle; skor ditandai `assisted` |
| R7 | False positive honeypot ngehukum orang jujur | 🟡 MEDIUM | Honeypot = dimensi skor, bukan gate |

**Q&A defense:** lihat `AUDIT.md` §10 (script jawaban juri).

---

## 11. Architecture Decision Records

| ADR | Judul | Status |
|---|---|---|
| 001 | Model selection (Flash vs Pro) | Accepted |
| 002 | Deterministic hybrid guardrails vs pure LLM scoring | Accepted |
| 003 | Client-side ML (MediaPipe) vs server-side proctoring | Accepted |
| 004 | Role taxonomy seed + auto "Others" | Accepted |
| 005 | Honeypot: deterministic catalog + generative variation | Accepted |

Detail di `docs/adrs/`.
