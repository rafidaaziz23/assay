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
 │   │     (DAG SkillTree visualizer)│                 │   • Audio/Timer controller  │   │
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
│   │  • Google Cloud Logging (Interrogation audit log as judge validation evidence)  │   │
│   │  • Artifacts & Static Storage (Google Cloud Storage)                           │   │
│   └────────────────────────────────────────────────────────────────────────────────┘   │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Technology Details & Feature Mapping

The table below maps each technology used to its recommended version, the rationale for choosing it, and the specific features it supports:

| Layer / Category | Component / Library | Version | Used for Which Features? | Rationale & Technical Justification |
|---|---|---|---|---|
| **Frontend Framework** | **Next.js** (App Router) | `15.x` | Main dashboard structure, routing between learning pages, and responsive layout. | Modern industry standard, fast rendering, flexible SSR/CSR, easy integration with Cloud Run / Vercel. |
| **Language (UI)** | **TypeScript** | `5.x` | Guarantees type safety for data contracts between UI and Backend. | Prevents typo bugs when parsing scores, node status, and JSON responses from the AI. |
| **Styling & Icons** | **Tailwind CSS + Lucide React** | `3.4+` | Dark/light theme, split-screen layout, lock icon 🔒, green checkmarks, and red alert modals. | Clean, modern UI built in minutes without heavy hand-written CSS overhead. |
| **Graph Visualizer** | **React Flow** (`@xyflow/react`) | `12.x` | **Mastery Skill Tree (DAG)**: renders interconnected material nodes (Yellow = Active, Gray = Locked, Green = Mastered). | The most interactive, performant graph visualization library; supports animated dependency edges between materials. |
| **Client-Side Telemetry** | **Custom Hook** (`useFriction`) | Native JS | **Copy-Paste & Keystroke Detection**: measures paste timing and typing speed while the user answers. | Flags long text appearing instantly in 0ms (`paste_detected: true`) as evidence of non-manual input. |
| **Backend Framework** | **FastAPI** (Python) or **Express.js** (TypeScript) | Python `3.11` / Node `20` | API server endpoints (`/modules/ingest`, `/interrogate/turn`, `/finalize`). | **Recommendation: FastAPI** — Python integrates with PyMuPDF and the Google AI SDK quickly and with minimal *boilerplate*. |
| **Document Parser** | **PyMuPDF (`fitz`)** or **LangChain TextSplitter** | `1.24+` | **PDF/Text Ingestion**: reads curriculum PDF documents and splits them into 300–500 word *chunks*. | PDF text extraction is fast (< 50ms per page) and accurate without breaking paragraph structure. |
| **Primary AI Engine** | **Google Gemini 2.5 Flash** | Model API | **1. Socratic Interrogator**<br>**2. Honeypot Injection**<br>**3. Evaluator Reasoning** | Blazing latency (< 800ms per turn), token-efficient, strong reasoning, and satisfies the Google Cloud mandatory requirement. |
| **AI SDK & Protocol** | **`google-genai`** (Google Gen AI SDK) | Official | Connects the backend to the Gemini API via Vertex AI or Google AI Studio. | Google's latest official SDK, supporting the `response_schema` parameter for pure JSON. |
| **Structured Output** | **Pydantic (Python) / Zod (TS)** | Pydantic v2 | **Deterministic JSON Schema**: guarantees Gemini output is structured JSON with no markdown wrapper. | Prevents the JSON parsing errors (`JSON.parse error`) that commonly sink hackathon demos in front of judges. |
| **Session State** | **In-Memory Dict / SQLite** | Built-in | Stores the user's learning session state (interrogation chat history, unlocked node status). | No cloud database setup, which would burn configuration time in a 4-day sprint. |
| **Demo Resilience** | **Local Cache Mock (`DEMO_MODE`)** | Custom JSON | **Offline Fallback Engine**: serves simulated responses when the API quota runs out or the network throws an HTTP 429. | Guarantees a 100% anti-blank live demo during judging (mirroring the winning pattern of *Chop* & *KalaSarthi*). |
| **Hosting & Container** | **Google Cloud Run** | Serverless | Hosts the backend and frontend Docker images in the Singapore region (`asia-southeast1`). | **Mandatory competition requirement**; auto-scale to zero, automatic HTTPS, direct Cloud Logging integration. |
| **Benchmarking Suite** | **Python Benchmark Script** | `requests` / `time` | **`benchmarks/` folder**: measures mean latency, P95, and honeypot accuracy over a 50-request loop. | **The key to locking in the Technical Merit score (40%)**, mirroring the previous 1st-place winning formula (*Padayon Ko*). |

---

## 3. Inter-Component Communication Flow (Step-by-Step Data Pipeline)

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

## 4. Why This Architecture Holds Up in Front of the Judges

1. **Meets 100% of the Organizers' Mandatory Requirements:**
   Uses **Google Gemini 2.5 Flash** as the primary engine and is hosted on **Google Cloud Run**. No competitor libraries (`openai`, `anthropic`) are installed in the dependencies.
2. **Deterministic Guardrails (Not Just Prompts):**
   Scoring is not just an AI inventing numbers; it combines **client-side telemetry (paste detection) + discrete category classification (Critical vs Copypaste)**. This answers the judges' concern about "AI that hallucinates grades".
3. **High Resilience (Offline Simulation):**
   With the `DEMO_MODE=cached` flag, the app keeps running smoothly even when judges test it without a stable API connection.
