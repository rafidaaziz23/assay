# Technical Architecture & Technology Stack Specification
## CogniForge: Active Socratic Learning Engine

**Event:** AI Builder Cup 2026 (Google Cloud x Hack2skill)  
**Target Deployment:** Google Cloud Run (Region: `asia-southeast1` Singapore)  
**Primary Engine:** Google Gemini 2.5 Flash  

---

## 1. High-Level Architecture Diagram (C4 Component Level)

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                                   CLIENT LAYER (Browser)                               │
│                                                                                        │
│   ┌────────────────────────────────┐                 ┌─────────────────────────────┐   │
│   │   Next.js 15 App Router        │                 │   Interactivity & Friction  │   │
│   │   • Tailwind CSS + Lucide Icons│                 │   • Keystroke dynamics probe│   │
│   │   • React Flow / @xyflow/react │                 │   • Paste event telemetry   │   │
│   │     (Visualisasi DAG SkillTree)│                 │   • Audio/Timer controller  │   │
│   └────────────────────────────────┘                 └─────────────────────────────┘   │
└───────────────────────────────────────────┬────────────────────────────────────────────┘
                                            │ HTTPS / REST / Server-Sent Events (SSE)
                                            ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                              BACKEND LAYER (Google Cloud Run)                          │
│                                                                                        │
│   ┌────────────────────────────────────────────────────────────────────────────────┐   │
│   │  FastAPI (Python 3.11) / Node.js Express Service                               │   │
│   │                                                                                │   │
│   │  ┌───────────────────────┐  ┌───────────────────────┐  ┌────────────────────┐  │   │
│   │  │ Document Chunking     │  │ Session State Machine │  │ Deterministic      │  │   │
│   │  │ • PyMuPDF / pdfplumber│  │ • In-Memory / SQLite  │  │ Scorer & Guardrails│  │   │
│   │  │ • Recursive splitter  │  │ • Node lock lifecycle │  │ • Anti-Hallucinate │  │   │
│   │  └───────────────────────┘  └───────────────────────┘  └────────────────────┘  │   │
│   │                                                                                │   │
│   │  ┌──────────────────────────────────────────────────────────────────────────┐  │   │
│   │  │ Fallback Controller: `DEMO_MODE=cached` (Zero-Crash Assurance)           │  │   │
│   │  └──────────────────────────────────────────────────────────────────────────┘  │   │
│   └───────────────────────────────────────┬────────────────────────────────────────┘   │
└───────────────────────────────────────────┼────────────────────────────────────────────┘
                                            │ gRPC / HTTPS (Official Google Gen AI SDK)
                                            ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                              GOOGLE CLOUD AI ECOSYSTEM                                 │
│                                                                                        │
│   ┌────────────────────────────────────────────────────────────────────────────────┐   │
│   │  Google Gemini 2.5 Flash Engine                                                │   │
│   │  • Structured Outputs (Native JSON Schema Enforcement)                         │   │
│   │  • Multi-Turn Socratic Interrogation Agent                                     │   │
│   │  • Honeypot Synthetic Concept Infiltration                                    │   │
│   │  • Reasoning Trace Classifier (Critical vs Copypaste vs Guess)                 │   │
│   └────────────────────────────────────────────────────────────────────────────────┘   │
│                                                                                        │
│   ┌────────────────────────────────────────────────────────────────────────────────┐   │
│   │  Google Cloud Observability                                                    │   │
│   │  • Google Cloud Logging (Audit log interogasi untuk bukti validasi juri)        │   │
│   │  • Artifacts & Static Storage (Google Cloud Storage)                           │   │
│   └────────────────────────────────────────────────────────────────────────────────┘   │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Rincian Detail Teknologi & Pemetaannya ke Fitur

Berikut adalah tabel pemetaan lengkap teknologi yang digunakan, versi yang direkomendasikan, alasan pemilihan, dan fitur spesifik yang didukung:

| Layer / Kategori | Komponen / Library | Versi | Dipakai untuk Fitur Apa? | Alasan & Justifikasi Teknis |
|---|---|---|---|---|
| **Frontend Framework** | **Next.js** (App Router) | `15.x` | Struktur utama dashboard, routing antar halaman belajar, dan layout responsif. | Standar industri modern, render cepat, SSR/CSR fleksibel, integrasi mudah dengan Cloud Run / Vercel. |
| **Language (UI)** | **TypeScript** | `5.x` | Menjamin type safety kontrak data antara UI dan Backend. | Mencegah bug typo pada parsing skor, status node, dan response JSON dari AI. |
| **Styling & Icons** | **Tailwind CSS + Lucide React** | `3.4+` | Tampilan tema gelap/terang, layout split-screen, ikon gembok 🔒, centang hijau, dan modal alarm merah. | Pembuatan UI bersih dan modern dalam hitungan menit tanpa overhead CSS manual yang rumit. |
| **Graph Visualizer** | **React Flow** (`@xyflow/react`) | `12.x` | **Mastery Skill Tree (DAG)**: Menampilkan node materi yang saling terhubung (Kuning = Active, Abu-abu = Locked, Hijau = Mastered). | Library visualisasi graf paling interaktif, performan, mendukung animasi garis dependensi antar materi. |
| **Client-Side Telemetry** | **Custom Hook** (`useFriction`) | Native JS | **Deteksi Copy-Paste & Keystroke**: Mengukur waktu paste dan kecepatan ketik user saat mengisi jawaban. | Mengidentifikasi jika teks panjang muncul instan dalam 0ms (`paste_detected: true`) untuk bukti input non-manual. |
| **Backend Framework** | **FastAPI** (Python) atau **Express.js** (TypeScript) | Python `3.11` / Node `20` | Server API endpoint (`/modules/ingest`, `/interrogate/turn`, `/finalize`). | **Rekomendasi: FastAPI** karena integrasi Python dengan PyMuPDF dan SDK AI Google sangat cepat dan minim *boilerplate*. |
| **Document Parser** | **PyMuPDF (`fitz`)** atau **LangChain TextSplitter** | `1.24+` | **PDF/Text Ingestion**: Membaca dokumen PDF kurikulum dan memecahnya menjadi *chunks* 300–500 kata. | Ekstraksi teks dari PDF sangat cepat (< 50ms per halaman) dan akurat tanpa merusak struktur paragraf. |
| **Primary AI Engine** | **Google Gemini 2.5 Flash** | Model API | **1. Socratic Interrogator**<br>**2. Injeksi Honeypot**<br>**3. Evaluator Reasoning** | Latensi kilat (< 800ms per turn), hemat biaya token, penalaran kuat, dan memenuhi syarat mutlak juri Google Cloud. |
| **AI SDK & Protocol** | **`google-genai`** (Google Gen AI SDK) | Official | Penghubung backend ke Gemini API via Vertex AI atau Google AI Studio. | SDK resmi generasi terbaru dari Google yang mendukung parameter `response_schema` untuk JSON murni. |
| **Structured Output** | **Pydantic (Python) / Zod (TS)** | Pydantic v2 | **Deterministic JSON Schema**: Menjamin output Gemini berupa format JSON terstruktur tanpa markdown wrapper. | Mencegah error parsing JSON (`JSON.parse error`) yang sering membuat demo hackathon gagal di hadapan juri. |
| **Session State** | **In-Memory Dict / SQLite** | Built-in | Menyimpan status sesi belajar pengguna (riwayat chat interogasi, status node yang terbuka). | Tidak memerlukan setup database cloud yang memakan waktu konfigurasi dalam sprint 4 hari. |
| **Demo Resilience** | **Local Cache Mock (`DEMO_MODE`)** | Custom JSON | **Offline Fallback Engine**: Menyajikan respons simulasi jika kuota API habis atau internet lempar error HTTP 429. | Menjamin live demo 100% anti-blank saat dinilai oleh dewan juri (meniru pola juara *Chop* & *KalaSarthi*). |
| **Hosting & Container** | **Google Cloud Run** | Serverless | Menghosting image Docker backend dan frontend di region Singapura (`asia-southeast1`). | **Syarat mutlak kompetisi**; auto-scale to zero, mendukung HTTPS otomatis, terhubung langsung ke Cloud Logging. |
| **Benchmarking Suite** | **Python Benchmark Script** | `requests` / `time` | **Folder `benchmarks/`**: Mengukur mean latensi, P95, dan tingkat akurasi Honeypot dari 50 request loop. | **Kunci mengunci nilai Technical Merit (40%)**, meniru formula kemenangan juara 1 terdahulu (*Padayon Ko*). |

---

## 3. Alur Komunikasi Antar Komponen (Step-by-Step Data Pipeline)

```
1. USER UPLOAD
   [Browser: PDF File]
          │ (POST multipart/form-data)
          ▼
   [Backend: PyMuPDF Chunking Service]
          │ Memecah PDF menjadi 3 Chunk Node
          ▼
   [State Machine: Node 1 = ACTIVE_READING, Node 2 & 3 = LOCKED]
          │ (Kembalikan JSON Graph)
          ▼
   [Frontend: React Flow me-render Skill Tree]

2. FEYNMAN GATEKEEPING
   [Browser: User mengetik rangkuman mandiri]
          │ (POST /nodes/:id/gate/verify)
          ▼
   [Backend memanggil Gemini 2.5 Flash]
          │ Prompt: "Apakah rangkuman ini menangkap esensi materi?"
          ▼
   [Jika lolos: Status berubah jadi INTERROGATE]

3. SOCRATIC & HONEYPOT INTERROGATION (THE CLIMAX)
   [Browser: User menjawab pertanyaan kasus]
          │ (POST /interrogate/turn + paste_telemetry)
          ▼
   [Backend menyuntikkan System Prompt + Honeypot Catalog]
          │ Prompt memuat instruksi menyisipkan istilah fiktif
          ▼
   [Gemini 2.5 Flash menghasilkan JSON Structured Response]
          │ Format: { interrogator_response, honeypot_active, honeypot_term }
          ▼
   [Frontend menampilkan pertanyaan Socratic di Terminal]

4. EVALUATION & NODE UNLOCK
   [User merespons Honeypot: Kritis vs Copas ChatGPT]
          │ (POST /interrogate/finalize)
          ▼
   [Deterministic Scorer]
          │ • Jika menolak konsep fiktif -> Reasoning = 100
          │ • Jika menyalin halusinasi AI luar -> Alert Merah + Reasoning = 0
          ▼
   [State Machine membuka kunci Node 2 jika Skor >= 75%]
          │
          ▼
   [Frontend: Animasi gembok Node 2 terbuka 🔓 dan Node 1 jadi hijau]
```

---

## 4. Keunggulan Arsitektur Ini di Hadapan Dewan Juri

1. **Memenuhi 100% Syarat Mutlak Panitia:**
   Menggunakan **Google Gemini 2.5 Flash** sebagai otak utama dan dihosting di **Google Cloud Run**. Tidak ada library kompetitor (`openai`, `anthropic`) yang terpasang di dependensi.
2. **Deterministic Guardrails (Bukan Cuma Prompt Biasa):**
   Penilaian bukan semata-mata AI mengarang angka, melainkan kombinasi **telemetri client-side (paste detection) + klasifikasi kategori diskrit (Critical vs Copypaste)**. Ini menjawab kekhawatiran juri mengenai "AI yang suka berhalusinasi memberi nilai".
3. **Resiliensi Tinggi (Offline Simulation):**
   Dengan adanya flag `DEMO_MODE=cached`, aplikasi tetap berjalan mulus meskipun juri menguji tanpa koneksi API yang stabil.
