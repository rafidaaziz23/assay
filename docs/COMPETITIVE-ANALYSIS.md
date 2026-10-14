# Intel & Deep Research: Lanskap Kompetitor AI Builder Cup 2026

**Dokumen Intelijen Kompetisi — v2.0.0**
**Produk:** **Assay** — The Active Socratic Learning Engine
*(codename repo: Active Learning Engine — `active-learning-engine/`)*
**Event:** Google Cloud x Hack2skill — AI Builder Cup 2026 (JAPAC Regional)
**Track:** **Track 4 — Media, Content & Digital Experiences (Adaptive Learning) — SATU TRACK SAJA**
**Target Submission:** **18 Oktober 2026, 23:59 UTC+8** (HARD DEADLINE)
**Fokus Riset:** Kompetitor aktif 2026, profil pemenang terdahulu (Gen AI Exchange), dan vulnerability assessment

> **Changelog dari v1 dokumen ini:** nama produk CogniForge → **Assay**; Track 4 **dan** Track 5 → **Track 4 saja** (aturan: 1 tim = 1 track); deadline 19 → **18 Oktober 2026**; flow lama (upload PDF wajib → chunk 300-600 kata → concept node) → **flow v2** (intent + role + PDF opsional → checklist realtime → silabus chapter); dual-metric → **single score + calibration gap**; DAG Skill Tree → **chapter stepper linear**; coding arena Monaco/Piston → **CUT ke roadmap**; honeypot dari gate keras → **dimensi skor**.
> Semua angka di dokumen ini berasal dari `reza-research/parts10/HASIL-TES-EMPIRIS.md` atau studi eksternal bernama. Tidak ada angka karangan.

---

## 1. Peta Kompetitor Langsung AI Builder Cup 2026 (Live Reconnaissance)

Dari penelusuran repositori publik peserta AI Builder Cup 2026, ada **dua kompetitor berbobot tinggi** yang sudah membangun agresif dan menetapkan standar tinggi. Keduanya di track berbeda dari Assay — jadi mereka bukan lawan head-to-head, tapi mereka adalah **patokan kualitas** yang akan dibandingkan juri.

```
┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                   LANSKAP KOMPETITOR AKTIF 2026                                 │
├───────────────────────────────┬─────────────────────────────────┬───────────────────────────────┤
│ PARAMETER                     │ FOREMAN (@arnavbee)             │ CHOP / CHOPDESK (@CrimsonS)   │
├───────────────────────────────┼─────────────────────────────────┼───────────────────────────────┤
│ Track                         │ Track 5: Future of Work         │ Track 1: BFSI                 │
│ Tagline / Masalah             │ "Agent that hires & vets agents"│ "Don't pay until it's chopped"│
│                               │ Tata kelola agen enterprise     │ Fraud invoice & vendor-swap   │
│ Tech Stack                    │ Python, ADK 2.x, A2A Protocol,  │ Next.js 15, TypeScript,       │
│                               │ Gemini 2.5 Pro/Flash, Cloud Run │ Gemini 2.5 Flash, Cloud Run SG│
│ Ukuran Repo                   │ 43 files                        │ 63 files                      │
│ Keunggulan Fatal              │ • Honesty canary & test probes  │ • Masalah lokal JAPAC nyata   │
│                               │ • Demo punya "villain" ditolak  │ • Heuristic offline fallback  │
│                               │ • Video script per-detik rapi   │ • Route /brief auto-generate  │
│ Titik Lemah                   │ Masalah terlalu abstrak/futuristik, Tidak ada kode execution sandbox,│
│                               │ value ekonomi saat ini belum riil segmen sangat sempit B2B AP │
└───────────────────────────────┴─────────────────────────────────┴───────────────────────────────┘
```

### Deep Dive 1: FOREMAN (The Apex Threat in Enterprise Track)

- **Arsitektur:** protokol *Agent-to-Agent (A2A)* dengan siklus:
  `Plan → Discover → Vet → Delegate → Verify → Deliver (+ hash-chained audit ledger)`
- **Trik Demo yang Memikat Juri:** mereka membuat **"Villain Agents"** di dalam registry demo:
  1. `quickfix` — agen pemalas yang menjawab *"Done"* untuk semua tugas tanpa eksekusi.
  2. `oracle` — agen yang selalu menjawab sangat meyakinkan tapi 100% berhalusinasi.
  *Di depan kamera, Foreman menangkap basah dan menolak kedua agen ini menggunakan **"Honesty Canary"** — soal yang jawabannya sengaja tidak ada.*
- **Reliability:** `FOREMAN_FAKE_LLM=1` untuk dev tanpa API key. Demo tidak pernah mati.
- **Pelajaran untuk Assay:**
  Mekanisme **honeypot** Assay punya DNA yang sama dengan **Honesty Canary** milik Foreman. Bedanya satu kalimat: **Foreman menguji kejujuran agen AI; Assay menguji kejujuran manusia yang menyontek AI lain.** Ini posisi filosofis yang kuat — sebut eksplisit di deck dan di Q&A. Kalau juri sudah melihat Foreman, mereka akan langsung mengenali polanya dan menilai Assay sebagai cermin sisi-manusia dari mekanisme yang sama.

### Deep Dive 2: CHOPDESK (The Localization Master in BFSI)

- **Masalah Nyata:** staf purchasing di UKM importir Asia Tenggara (Singapura, Penang, dsb) masih membayar faktur ratusan juta via WhatsApp dan email PDF, di mana rekening vendor rawan dipalsukan.
- **Trik Engineering:** **heuristic fallback.** Kalau Gemini API kena rate limit HTTP 429 atau koneksi mati, aplikasi otomatis beralih ke analisis graf vendor lokal dengan pesan: *"(Gemini unreachable — local vendor graph used.)"*. **Demo mereka 0% risiko blank.**
- **Pelajaran untuk Assay:**
  Assay **wajib** punya kelas fallback yang sama: `DEMO_MODE=cached` (env) **atau** header `x-demo-mode: cached`, plus trigger otomatis saat Gemini balikin 429/500/503. Dua skenario pre-cached yang harus ada: **success flow** (`CRITICAL_REJECTION`, skor tinggi, chapter unlock) dan **caught flow** (`AI_HALLUCINATION_COPYPASTE`, skor turun, integrity flag). Banner `LOCAL_DETERMINISTIC_CACHE` boleh ditampilkan di depan kamera — itu fitur, bukan glitch.

---

## 2. Bedah DNA Pemenang Hackathon Google Cloud Terdahulu (Historical Champions)

Menganalisis pemenang resmi *Google Cloud Gen AI Exchange* dan pemenang regional APAC memberi cetak biru apa yang **sebenarnya dinilai juri Google Cloud**:

| Pemenang & Tahun | Kategori / Track | Tech Stack Kunci | Rahasia Menang (*The Winning Factor*) |
|---|---|---|---|
| **Padayon Ko**<br>*(Juara 1 APAC 2024)* | EdTech / Social Impact (Filipina) | Gemini API, Google Chirp STT, Synthesize TTS, Flask, Cloud Run | **Folder `benchmarks/`:** laporan pengujian latensi 100 request (mean 2850 ms, SD 436 ms). Dilengkapi notebook TAM/SAM/SOM dan adopsi nyata 500 siswa di Lapu-Lapu City. |
| **Savour AI**<br>*(Juara 2 APAC 2024)* | FoodTech (Australia) | Gemini 2.0 Flash/Pro, LangGraph, MongoDB Atlas, Streamlit | **ADR formal:** 4 dokumen keputusan, berani menolak Google Agent Builder ("terlalu kaku") dan memilih LangGraph. Hanya menampilkan 3 fitur MVP, sisanya roadmap. |
| **Team Skippers**<br>*(Juara 1 Pro 2025)* | Future of Work (Enterprise QA) | Gemini Pro, Automated Test Framework | Menghubungkan spesifikasi regulasi medis ke eksekusi unit test otomatis. Menyelesaikan masalah compliance yang bernilai miliaran rupiah. |
| **May The Agents Be With You**<br>*(Juara 1 Pro 2025)* | Manufacturing Operations | Multi-Agent Orchestration, Industrial IoT | Bekerja sama langsung dengan JK Cement untuk optimasi konsumsi energi pabrik semen secara otonom. |
| **KalaSarthi**<br>*(Finalis Unggulan 2025)* | Retail / Artisans (India) | Next.js 15, Gemini 2.0 Flash + Nano, Firebase, Redis | **3-Tier Offline-First Architecture:** `Gemini Flash (Online)` → `Gemini Nano (On-Device)` → `SimpleOfflineAI (Fallback)`. Tahan banting tanpa koneksi internet. |
| **YouthMind**<br>*(Juara 1 Student 2025)* | Mental Health | Vanilla HTML/JS, 12 audio mp3 (18 file, TANPA README) | **Storytelling & Empathy:** jumlah baris kode kalah penting dibanding kekuatan delivery pitch 3 menit. |

**Pola yang relevan untuk Assay:**

- Padayon Ko menang dengan **folder `benchmarks/`** — Assay punya `eval/` + `benchmarks/` dengan angka honeypot empiris (n=80). Ini persis jenis bukti yang sama.
- Savour menang dengan **ADR + disiplin scope** — Assay punya ADR 001-005 dan daftar cut yang eksplisit (§8 PRD). Jangan sembunyikan cut list; tampilkan sebagai bukti disiplin.
- KalaSarthi menang dengan **fallback berlapis** — Assay punya `DEMO_MODE=cached` + grounding cache + deterministic catalog honeypot.
- YouthMind menang dengan **delivery** — video 3 menit Assay sudah ditulis per-detik. Script ditulis sebelum rekaman, bukan sesudah.

---

## 3. Mitos vs Fakta Hackathon Google Cloud

```
┌──────────────────────────────────────────────┬──────────────────────────────────────────────┐
│ MITOS UMUM PESERTA                           │ FAKTA EMPIRIS DI MEJA JURI                   │
├──────────────────────────────────────────────┼──────────────────────────────────────────────┤
│ "Harus bikin UI Next.js + shadcn mewah."     │ Savour juara 2 pakai Streamlit biasa.        │
│                                              │ YouthMind juara pakai HTML kosongan.         │
│ "Harus fine-tune model sendiri."             │ 100% pemenang pakai Gemini pre-trained.      │
│ "Harus bikin 10-15 fitur komprehensif."      │ Menampilkan 10 fitur setengah matang = drop. │
│                                              │ 3 fitur bekerja sempurna = juara.            │
│ "Harus pakai semua produk AI Google."        │ Savour tolak Agent Builder via ADR & menang. │
│                                              │ Yang penting: Gemini + Cloud Run wajib jalan.│
│ "Repo rapi pasti menang."                    │ YouthMind tanpa README juara 1; yang penting │
│                                              │ video pitch 3 menit & live demo jalan.       │
│ "Track banyak = peluang menang lebih besar." │ 1 tim = 1 track. Assay ambil Track 4 saja.   │
└──────────────────────────────────────────────┴──────────────────────────────────────────────┘
```

---

## 4. Analisis Titik Lemah Kompetitor (Vulnerability Assessment)

Bagaimana Assay bisa menang atas kompetitor di track lain maupun peserta sejenis?

### 1. Mayoritas Peserta Terjebak dalam "AI Helper Bias"

- **Kelemahan Lawan:** mayoritas peserta membangun bot serba membantu (*"Tanya saya apa saja, saya rangkumkan, saya buatkan kodenya"*).
- **Serangan Assay:** Assay satu-satunya yang mengambil posisi **AI Adversarial / Enforcer**. Yang diserang adalah fenomena nyata: *"Generative AI membuat generasi baru engineer malas berpikir kritis."* Kontrasnya ekstrem dan langsung diingat juri.

### 2. Kompetitor Track 5 (Foreman) Terlalu Konseptual

- **Kelemahan Foreman:** *"Agents hiring agents with Ed25519 signatures"* adalah solusi untuk dunia 5 tahun ke depan, saat perusahaan sudah punya ribuan agen otonom. Belum ada perusahaan JAPAC yang butuh itu hari ini.
- **Keunggulan Assay (Track 4):** degradasi pemahaman siswa/developer akibat AI terjadi **hari ini, jam ini**, di seluruh bootcamp dan universitas di Asia Tenggara. Relevansi pasarnya instan.
- **Catatan penting:** karena Assay sekarang **Track 4 saja**, Foreman tidak lagi lawan langsung — dia jadi **referensi kualitas dan sumber narasi** ("mekanisme yang sama, sisi manusia").

### 3. Kompetitor Terdekat di Track 4: Incumbent Komersial, Bukan Peserta

- **Khanmigo / Google Learn About:** Socratic tapi *suggestive*. User bisa minta jawaban langsung, tidak ada gatekeeping, tidak ada deteksi integritas, tidak bisa upload PDF sendiri. Assay = *enforcement engine*, bukan tutor sugestif.
- **NotebookLM / ChatGPT:** perpustakaan dan dispenser jawaban. NotebookLM menelan dokumen tapi tidak pernah menginterogasi pemiliknya. Assay membalik arah pertanyaan.
- **Coursera / Udemy:** progres berbasis penyelesaian konten, bisa di-skip bebas, nol verifikasi penalaran.

### 4. Jebakan Dependensi Terlarang (The Disqualification Trap)

- Riset menemukan peserta seperti *Artifind* tidak lolos karena menulis *"[OI]/Claude for text generation"* di README.
- Repositori *Padayon Ko* pernah membocorkan token Facebook aktif di `.env.example`.
- Peserta lain ke-commit `.env`, menaruh build output `dist/` (90 dari 157 file), dan tidak konsisten menyebut nama produk sendiri (README "LegalEase AI" vs dokumen "LegalMind AI").
- **Prosedur Keamanan Assay:**
  - `package.json` / `requirements.txt` bersih 100% dari package `openai`, `anthropic`, `cohere`.
  - Hanya `@google/genai` atau `@google/generative-ai`; model Google saja (Gemini/Gemma).
  - Deploy **wajib** di Cloud Run (atau Firebase).
  - `.env.example` pakai dummy credential, `.env` tidak pernah masuk repo.
  - **Satu nama produk di semua artefak: Assay.** Codename repo `active-learning-engine/` boleh tetap, tapi UI, README, deck, video semua bilang **Assay**.

---

## 5. Matriks Perbandingan: Assay vs Kompetitor Kunci

| Dimensi Evaluasi | Foreman (`arnavbee`) | Chopdesk (`CrimsonSithria`) | Khanmigo / NotebookLM | **Assay (Proyek Kita)** |
|---|---|---|---|---|
| **Track** | Track 5 (Future of Work) | Track 1 (BFSI) | Pasar edukasi komersial | **Track 4 (Media, Content & Digital Experiences) — satu-satunya track** |
| **Peran AI** | Auditor agen | Verifikator pembayaran | Tutor sugestif / perpustakaan | **Interrogator — mempertanyakan jawaban user** |
| **Core Moat** | A2A Protocol & Ed25519 | Vendor Lookalike Graph | Knowledge base + Socratic chat | **Honeypot injection + gated chapter + calibration gap** |
| **Mekanisme "Uji Kejujuran"** | "Honesty Canary" — fakta yang tidak ada, untuk agen AI | Vendor master match | Tidak ada | **Honeypot — konsep fiktif, untuk manusia yang nyontek AI** |
| **Demo "Villain"** | Agen palsu `quickfix` & `oracle` | Invoice fiktif CEO fraud | Tidak ada (selalu pasif) | **Siswa yang copas jawaban LLM luar — tertangkap basah** |
| **Integritas** | Hash-chained audit ledger | Vendor master match | Nol (mudah di-cheat) | **Honeypot score dimension + Focus Mode (MediaPipe on-device)** |
| **Fallback saat API mati** | `FOREMAN_FAKE_LLM=1` | Heuristic vendor graph lokal | N/A | **`DEMO_MODE=cached` + header `x-demo-mode: cached` + grounding cache** |
| **Kelemahan Utama** | Pasar belum siap, value belum riil hari ini | Ruang lingkup terlalu sempit | Mendorong kemalasan kognitif | Perlu disiplin membatasi scope 4 hari |
| **Peluang Menang** | Sangat tinggi (Track 5) | Tinggi (Track 1) | N/A (incumbent) | **Sangat tinggi (Track 4)** |

### 5.1 Matriks Diferensiasi Assay vs Incumbent (Flow v2)

| | Coursera / Udemy | ChatGPT / NotebookLM | Khanmigo | **Assay** |
|---|---|---|---|---|
| Peran AI | Penyampai konten | Dispenser jawaban | Tutor sugestif | **Interrogator** |
| Tombol ringkasan | Video, tanpa sintesis | Satu klik | Tersedia | **Tidak ada** |
| Progresi | Skip bebas | Skip bebas | Skip bebas | **Terkunci sampai penalaran lulus (skor ≥ 75)** |
| Cek integritas | Tidak ada | Tidak ada | Tidak ada | **Honeypot + Focus Mode** |
| Bantuan di dalam materi | Forum | Chat terpisah | Chat | **Select kata → tanya AI (Socratic)** |
| Masuk materi sendiri | Modul vendor | Upload dokumen | Tidak | **PDF opsional, page-anchored (PDF-RAG)** |
| Metrik sukses | Completion | Kelancaran | Engagement | **Skor + calibration gap** |

---

## 6. Yang Baru di Assay v2 (dan Kenapa Itu Bukan Fitur Tambahan)

Ini bukan daftar fitur. Ini yang membedakan Assay v2 dari v1 dan dari incumbent, dalam urutan flow:

1. **Intake intent-first, bukan upload-first.** User mulai dari niat belajar + role (Frontend/Backend/Fullstack/DevOps/Data-ML/Mobile/QA-Test/Security/System Design), dengan opsi **`Others`** muncul otomatis kalau niat tidak match seed mana pun (ADR 004). PDF **opsional** — tanpa PDF, chapter di-generate dari role taxonomy dan ditandai `source: generated`. Incumbent lain menuntut dokumen dulu.
2. **Checklist realtime yang bisa diedit user.** Item streaming lewat SSE (`checklist.partial`), masing-masing bertag `document` / `role_taxonomy` / `grounded_external`. Item yang tidak dicentang **tidak pernah jadi chapter**. Rencana belajar jadi milik user, bukan milik model.
3. **PDF-RAG wajib + Google Search grounding opsional.** Setiap chapter punya page-anchor ke dokumen. Ini yang bikin klaim honeypot bisa diverifikasi ("istilah ini tidak ada di halaman mana pun modulmu"). Grounding eksternal dibatasi 1-2 chapter dan **di-cache**, supaya demo tidak bergantung jaringan.
4. **Inline select-word → tanya AI (Socratic).** User select satu kata atau frasa di dalam chapter → popover. AI **balik bertanya / kasih hint / menunjuk halaman**, bukan memberi definisi. Field `gave_direct_answer: false` tampil di panel respons. Select beberapa kata → muncul **suggested questions**. Ini tesis "anti brain-rot" dalam bentuk interaksi terkecil.
5. **Interview quiz per chapter + honeypot sebagai dimensi skor.** 2-3 ronde pertanyaan inferensial (bukan "apa definisi X") dengan follow-up adaptif. Satu konsep fiktif diselipkan per chapter. Klasifikasi deterministik → skor: **`CRITICAL_REJECTION` +2**, **`AI_HALLUCINATION_COPYPASTE` −2**, **`UNVERIFIED_HONEST` 0**, **`EVASIVE` −1**. **Bukan gate** — yang menentukan unlock tetap `chapter_score >= 75`. Gate keras akan menghukum pelajar jujur yang bilang "saya tidak tahu" (ADR 002).
6. **Calibration gap.** Sebelum skor di-reveal, user memprediksi skornya sendiri. `calibration_gap = |predicted − actual|` jadi metrik utama laporan. Semua kompetitor melaporkan skor; tidak ada yang melaporkan **jarak antara "merasa siap" dan "benar-benar siap"**. Ini metrik yang membuka *illusory competence*.
7. **Focus Mode on-device (MediaPipe) + auto-blur.** Gaze/head-pose drift, jumlah wajah > 1, tab blur — semua inferensi di browser. Video **tidak pernah keluar device**; yang dikirim hanya event boolean (`video_transmitted: false`, ADR 003). Terdeteksi → halaman **auto-blur** + flag `assisted`. **Accessible Mode** bisa mematikan kamera → `assisted_unverified`, skor tetap dihitung. Dijual sebagai *integrity signal*, bukan klaim "tidak bisa dicurangi".

---

## 7. Yang CUT dari MVP (Pindah ke Roadmap — Tampilkan, Jangan Sembunyikan)

| Dibuang dari MVP | Alasan | Nasib |
|---|---|---|
| **Coding arena (Monaco + Piston + TDL)** | Tidak muat 4 hari; bukan wedge diferensiasi | Roadmap Phase 2 |
| **DAG Skill Tree visual (ReactFlow)** | Bukan pembeda; chapter stepper linear gratis dan lebih jelas | Roadmap Phase 2 |
| **Dual-metric (2 skor terpisah)** | Single score + calibration gap lebih murah dan lebih kuat demonya | Digantikan |
| Voice / Gemini Live | Latency + biaya berisiko di live demo | Roadmap Phase 2 |
| Auth kompleks / multi-user | 1 user demo cukup | Roadmap Phase 3 |
| Multi-source input (video/audio) | PDF sudah cukup buat demo | Roadmap Phase 2 |

**Yang WAJIB ada walaupun 4 hari** (ini yang mengangkat Technical Merit 40%): eval harness + angka, verifier loop, calibration, cached fallback, Focus Mode on-device.

---

## 8. Formula 5 Komponen Emas Submisi Juara

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                        5 KOMPONEN EMAS SUBMISI JUARA (CHECKLIST)                       │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ 1. `benchmarks/` + `eval/`                                                             │
│    Harness yang menjalankan honeypot & trap suite di atas model Google, dengan output  │
│    mentah tersimpan (JSONL) dan klasifikasi deterministik — bukan LLM judge.           │
│    Angka yang dipakai: 54% hallucination (n=80), fictional_term 100% (n=12 valid) /      │
│    trap_number 58% (n=48), verifier 13/20 (65%), structured JSON 4/4.                   │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ 2. `docs/adrs/` — ADR 001 sampai 005                                                   │
│    001 model selection (Flash vs Pro) · 002 deterministic hybrid guardrails vs pure    │
│    LLM scoring · 003 client-side MediaPipe vs server-side proctoring · 004 role        │
│    taxonomy seed + auto "Others" · 005 honeypot catalog deterministik + variasi        │
│    generatif. Tulis juga alternatif yang DITOLAK, bukan cuma keputusan yang diambil.   │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ 3. Fallback offline (`DEMO_MODE=cached`)                                               │
│    Env `DEMO_MODE=cached` ATAU header `x-demo-mode: cached` ATAU Gemini 429/500/503.   │
│    Dua skenario wajib: success flow (CRITICAL_REJECTION, unlock) dan caught flow       │
│    (AI_HALLUCINATION_COPYPASTE, integrity flag). Grounding eksternal juga di-cache.    │
│    Video dan live URL tidak boleh blank saat juri meninjau.                            │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ 4. Video demo 3 menit (180s, hard cap) — script ditulis dulu                           │
│    00:00-00:20  Masalah: 95% pakai AI, 67% bilang merusak cara berpikir.               │
│    00:20-00:50  Intake: intent + role (+ PDF opsional, lalu diulang dengan PDF).       │
│    00:50-01:15  Checklist realtime streaming, user uncheck satu item.                  │
│    01:15-01:40  Silabus + page-anchor + referensi grounded (cached: true).             │
│    01:40-02:05  Reader terkunci + select kata → AI balik bertanya.                     │
│    02:05-02:45  MOMEN EMAS: copas ke LLM luar → honeypot −2; tolak premis → +2.        │
│                 Focus Mode mendeteksi → auto-blur. Slider calibration diisi.           │
│    02:45-03:00  Reveal skor 88, threshold 75, calibration gap 2, laporan + appeal.     │
│    Tanpa logo, tanpa intro tim. Frame pertama adalah masalahnya.                       │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ 5. Pitch deck 10 slide, bahasa Inggris, PDF                                            │
│    Termasuk tabel kompetitor (dokumen ini §5), TAM/SAM/SOM bottom-up, roadmap 3 fase   │
│    dengan cut list ditampilkan sebagai disiplin scope, dan appendix provenance angka.  │
│    Setiap angka harus bisa ditelusuri. Kalau tidak ada di tabel provenance, tidak      │
│    masuk deck.                                                                         │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 9. Angka Bukti (Sumber Tunggal, Jangan Dikarang)

Sumber: `reza-research/parts10/HASIL-TES-EMPIRIS.md` — 14 Oktober 2026, gateway lokal, 5 workers, respons mentah di `results/*.jsonl`, klasifikasi regex heuristik (transparan, bukan LLM judge).

| Klaim | Angka | Sampel |
|---|---|---|
| Honeypot hallucination rate (semua model) | **54%** | n = 80 panggilan, 4 model |
| — gemini-3.8-flash-medium | 75% | 20 panggilan |
| — deepseek-v4-pro | 70% | 20 panggilan |
| — deepseek-v4-flash | 45% | 20 panggilan |
| — deepseek-v4.1-flash | 25% | 20 panggilan |
| Trap efektivitas: fictional_term | **100%** (10 comply / 0 pushback / 2 error) | n = 12 valid |
| Trap efektivitas: trap_number | 58% | n = 48 |
| Trap efektivitas: false_premise | 25% | n = 48 |
| Trap efektivitas: over_claim | 25% | n = 48 |
| Verifier loop menangkap halusinasi | 13/20 (65%) | 20 jawaban halusinasi |
| Structured output JSON valid | 4/4 (100%) | 4 panggilan schema |

**Yang tidak diklaim:**

- **Tidak ada angka latency** yang dipakai di deck atau video. Yang terukur di harness adalah probe ke gateway lokal (rata-rata 25s), itu mencerminkan harness, bukan produk.
- Angka P3 (diskriminasi judge, gap 75-85 poin) ada di sumber tapi tidak dipakai sebagai klaim produk.
- Deck v1 pernah menulis "91.3% capture rate" dan "640 ms latency"; demo script v1 pernah menulis "sub-1.2s P95". **Ketiganya tanpa sumber dan tidak boleh muncul lagi** dalam bentuk apa pun.
- Honeypot adalah **dimensi skor**, bukan gate keras.

---

## 10. Daftar Periksa Sebelum Submit (18 Oktober 2026)

- [ ] **Konsistensi nama:** tidak ada sisa string "CogniForge" di README, UI, deck, video, atau komentar kode. Semua bilang **Assay**.
- [ ] **Track statement:** deck dan submission form menyebut **Track 4** saja, tidak ada penyebutan Track 5.
- [ ] **Dependency audit:** tidak ada `openai` / `anthropic` / `cohere` di `package.json` atau `requirements.txt`; hanya paket Google.
- [ ] **Deploy:** Cloud Run live dan bisa diakses juri, dengan `DEMO_MODE=cached` siap sedia.
- [ ] **Secret hygiene:** `.env` tidak ke-commit; `.env.example` isinya dummy.
- [ ] **No build output:** `dist/` / `build/` / `node_modules` tidak masuk repo.
- [ ] **Repo berisi:** `benchmarks/`, `eval/`, `docs/adrs/001-005`, diagram arsitektur, tabel kompetitor + alasan beda.
- [ ] **Pisah tegas "sudah jadi" vs "roadmap":** cut list (§7) ditampilkan, bukan disembunyikan.
- [ ] **Video < 3 menit** dengan script per-detik, direkam dalam satu sesi.
- [ ] **Deck PDF 10 slide, bahasa Inggris.** Semua materi submisi bahasa Inggris.
- [ ] **Setiap angka punya sumber** di §9 atau studi bernama. Tidak ada angka karangan.
