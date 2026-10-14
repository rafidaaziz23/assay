# Assay: The Active Socratic Learning Engine

> **"Every AI study tool answers questions. Assay questions your answers."**

[![Event](https://img.shields.io/badge/AI%20Builder%20Cup-2026-blue.svg)](https://hack2skill.com)
[![Track](https://img.shields.io/badge/Track%204-Media%2C%20Content%20%26%20Digital%20Experiences-blueviolet.svg)](#)
[![Stack](https://img.shields.io/badge/Stack-React%20Vite%20%2B%20FastAPI%20%2B%20Gemini-orange.svg)](#)
[![Deploy](https://img.shields.io/badge/Deploy-Google%20Cloud%20Run-green.svg)](#)
[![Resilience](https://img.shields.io/badge/Zero--Crash-Deterministic%20Cache-emerald.svg)](#)

---

## 1. Executive Summary & The "Anti-AI-Brain-Rot" Manifesto

In the generative AI era, conventional learning platforms and static PDF modules face a crisis: **AI Brain Rot**. Students and junior engineers feed materials into ChatGPT or NotebookLM to produce instant summaries, multiple-choice quizzes, or boilerplate solutions without critical reasoning.

### The Consequences:
- **Atrophy of Critical Thinking:** Cognitive muscles remain unexercised.
- **Illusory Competence:** Learners believe they grasp complex systems because they read an AI-generated synthesis, only to collapse in real production scenarios.
- **Empirical Evidence (2026 Research):**
  - **95%** of students use AI (HEPI 2026).
  - **67%** admit AI degrades their independent reasoning capability (RAND, Mar 2026).
  - **OECD PISA 2025:** Lowest critical thinking scores in recorded history.
  - **Unguarded AI Assistants:** Cause student retention to drop by **17%**, whereas AI tutors that refuse direct answers and force reasoning eliminate cognitive degradation entirely (arXiv:2606.26181).

### The Solution: Assay
Assay flips the paradigm from a **"Passive Answer Dispenser"** into an **"Active Socratic Enforcer & Interrogator"** with a **High-Friction, High-Reward** philosophy:
1. **Intake First:** Begins with the learner's intent + target engineering role + optional PDF.
2. **Realtime Scope Checklist:** Live stream of topics categorized by origin (`document`, `role_taxonomy`, `grounded_external`) allowing user curation.
3. **Structured Syllabus:** Chunks the content into gated chapters anchored to page numbers.
4. **Gated Progression:** Subsequent chapters remain **LOCKED** until passing the chapter interview quiz (score &ge; 75).
5. **Inline Socratic Inquirer:** Selecting any keyword or phrase triggers Socratic counter-inquiry (`gave_direct_answer: false`).
6. **Synthetic Honeypot Injection:** Injects plausible fictitious concepts (e.g., *"React Quantum Hook"*, *"Zero-Latency Mutex"*) to catch external LLM copy-pasting.
7. **On-Device Focus Mode:** MediaPipe client-side telemetry detects gaze drift, multi-face presence, and tab switching, triggering auto-blur while preserving privacy (`video_transmitted: false`).
8. **Self-Calibration & Audit Report:** Requires learners to predict their score before reveal to measure the **Calibration Gap** (|predicted &minus; actual|).

---

## 2. System Architecture

```
+---------------------------------------------------------------------------------------+
|                                CLIENT LAYER (Browser)                                 |
|                                                                                       |
|   React 18 + Vite (TypeScript + Tailwind CSS)                                         |
|   • Intake Screen (Intent + Seed Role Selector + Optional PDF)                        |
|   • Realtime Checklist Stream (Live SSE / JSON)                                       |
|   • Linear Gated Chapter Reader (Inline Socratic Ask Popover)                         |
|   • Focus Mode Monitor (On-Device MediaPipe Signals, Auto-Blur, Accessible Mode)      |
|   • Self-Calibration Slider & Multi-Chapter Integrity Audit Report                    |
+---------------------------------------------------------------------------------------+
                                           │
                                           │ REST / JSON / SSE (Base: /api/v1)
                                           │ Resilience Header: x-demo-mode: cached
                                           ▼
+---------------------------------------------------------------------------------------+
|                            BACKEND LAYER (FastAPI / Cloud Run)                        |
|                                                                                       |
|   FastAPI (Python 3.11) + Uvicorn                                                     |
|   • Lifecycle State Machine: LOCKED -> ACTIVE_READING -> INTERVIEW -> SCORED          |
|                              -> UNLOCKED (>= 75) / NEEDS_REVIEW (< 75)                |
|   • PyMuPDF Document Extractor: Page-anchored chunking                                |
|   • Resilient Fallback Engine: Zero-crash cached simulation (DEMO_MODE=cached)        |
|   • Deterministic Honeypot Catalog: 4-state response classifier                       |
+---------------------------------------------------------------------------------------+
                                           │
                                           │ Google Gen AI SDK (google-genai)
                                           ▼
+---------------------------------------------------------------------------------------+
|                             GOOGLE CLOUD AI ECOSYSTEM                                 |
|                                                                                       |
|   Google Gemini 2.5 Flash Engine                                                      |
|   • Native JSON Schema Structured Outputs                                             |
|   • Multi-Turn Socratic Interrogator                                                  |
|   • Secondary Verifier Adjudicator (Gemini Pro)                                       |
+---------------------------------------------------------------------------------------+
```

---

## 3. Monorepo Directory Structure

```
assay/
├── README.md                 # Primary documentation, architecture & run guide
├── package.json              # Monorepo root scripts (dev:frontend, dev:backend, eval)
├── .gitignore                # Root gitignore (Python, Node, secrets, cache)
├── docs/                     # Specifications & Architecture Decision Records
│   ├── PRD.md                # Canonical Product Requirements Document v2.0.0
│   ├── API-CONTRACTS.md      # Locked API endpoints & JSON schema contracts
│   ├── ARCHITECTURE.md       # Technical architecture & stack mapping
│   ├── TEAM-TASK-DELEGATION.md # 3-Developer WBS & Day-by-Day schedule
│   ├── DEMO-SCRIPT.md        # 180s video storyboard & evidence card
│   ├── AUDIT.md              # Technical audit & judge Q&A defense
│   └── adrs/                 # ADR 001 through ADR 005
├── frontend/                 # DEV 1: React 18 + Vite + TypeScript + Tailwind CSS
│   ├── package.json
│   ├── vite.config.ts
│   ├── tailwind.config.js
│   ├── index.html
│   ├── src/
│   │   ├── types/api.ts      # Typed API contracts matching API-CONTRACTS.md
│   │   ├── services/api.ts   # API client with zero-blocker mock fallback
│   │   ├── mocks/*.json      # Offline mock payloads for all endpoints
│   │   ├── components/       # Stepper, Navbar, SocraticAsk, FocusMode, Calibration
│   │   ├── pages/            # Intake, Checklist, Syllabus, Reader, Interview, Report
│   │   ├── App.tsx
│   │   └── main.tsx
├── backend/                  # DEV 2: FastAPI + Python 3.11 + Google Gen AI SDK
│   ├── requirements.txt      # Strictly Google stack; NO openai/anthropic/cohere
│   ├── Dockerfile            # Cloud Run ready container (asia-southeast1)
│   ├── .env.example
│   ├── app/
│   │   ├── main.py           # FastAPI app, CORS, demo middleware
│   │   ├── config.py         # App settings & Gemini configuration
│   │   ├── core/             # State machine & deterministic fallback cache
│   │   ├── schemas/          # Pydantic v2 models strictly matching API contracts
│   │   ├── services/         # PyMuPDF parser, Honeypot catalog, Gemini service
│   │   └── api/v1/endpoints/ # Intake, Chapters, Interview, Calibration, Focus, Report
│   └── tests/                # Automated pytest endpoint tests
├── eval/                     # DEV 3: Automated Benchmark & Evaluation Harness
│   ├── README.md             # Benchmark methodologies & rubric weighting
│   ├── run_benchmarks.py     # Offline benchmark suite testing honeypot classification
│   └── results/              # Empirical audit results from research
└── prompts/                  # DEV 3: System prompts (Socratic, Honeypot, Verifier)
```

---

## 4. Setup & Running Instructions

### Prerequisites
- **Node.js**: v18+ (v20+ recommended)
- **Python**: 3.11+
- **Google AI Studio API Key**: (Optional if running in offline `DEMO_MODE=cached`)

---

### Backend Setup (FastAPI)

1. Open a terminal and navigate to `backend/`:
   ```bash
   cd backend
   ```
2. Create and activate a Python virtual environment:
   ```bash
   # Windows (PowerShell)
   python -m venv venv
   .\venv\Scripts\Activate.ps1

   # Linux / macOS
   python3 -m venv venv
   source venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Configure environment:
   ```bash
   cp .env.example .env
   ```
   *Edit `.env` to set your `GOOGLE_API_KEY`. If you don't have a key yet, set `DEMO_MODE=cached`.*
5. Run the server:
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```
6. Verify:
   - Interactive Swagger Docs: `http://localhost:8000/docs`
   - Healthcheck: `http://localhost:8000/health`

---

### Frontend Setup (React + Vite)

1. Open a second terminal and navigate to `frontend/`:
   ```bash
   cd frontend
   ```
2. Install packages:
   ```bash
   npm install
   ```
3. Configure environment:
   ```bash
   cp .env.example .env
   ```
4. Start development server:
   ```bash
   npm run dev
   ```
5. Open your browser at `http://localhost:5173`

---

### Running the Entire Monorepo

You can run both services from the root directory:
```bash
# Terminal 1 - Backend
npm run dev:backend

# Terminal 2 - Frontend
npm run dev:frontend
```

---

## 5. Zero-Crash Demo Resilience Mode

Live hackathon presentations frequently encounter API rate limits (`429`), network dropouts, or LLM latency spikes. To ensure a **100% reliable demo**:

1. **Backend Cache:** When `DEMO_MODE=cached` is set in `.env` or the client sends the header `x-demo-mode: cached`, the backend automatically serves local deterministic scenarios with zero external API calls.
2. **Frontend Mock Fallback:** If `VITE_USE_MOCK=true` or if the backend server is unreachable, the frontend intercepts requests and seamlessly loads from `frontend/src/mocks/*.json`.
3. **Banner Indicator:** The UI proudly displays `LOCAL_DETERMINISTIC_CACHE: Zero-crash fallback scenario engaged` — presenting resilience as an intentional engineering feature rather than a glitch.

---

## 6. Team Task Delegation (3-Developer Squad)

Based on [TEAM-TASK-DELEGATION.md](./docs/TEAM-TASK-DELEGATION.md) for the 4-day sprint leading to the **18 October 2026** deadline:

| Role | Developer Focus | Primary Directory | Core Deliverables |
|---|---|---|---|
| **DEV 1** | Frontend & UX | `frontend/` | Intake screen, Checklist UI, Linear Stepper, Socratic Ask popover, Focus Mode webcam UI, Calibration slider, Report dashboard. |
| **DEV 2** | Backend & Infrastructure | `backend/` | FastAPI routes (`/api/v1`), chapter state machine, PyMuPDF page-anchored extractor, `DEMO_MODE=cached` fallback, Cloud Run Dockerfile. |
| **DEV 3** | AI Engine, Prompts & Eval | `prompts/`, `eval/` | Google Gen AI SDK integration, Socratic prompts, 10-term deterministic honeypot catalog, secondary verifier loop (Gemini Pro), benchmark suite. |

---

## 7. Auditable Evaluation Benchmarks (Technical Merit 40%)

All metrics cited in our pitch deck originate from the automated evaluation suite (`eval/run_benchmarks.py`) and empirical audits:

| Dimension | Measured Value | Sample Size |
|---|---|---|
| **Honeypot Hallucination Rate (External Models)** | **54%** | n = 80 calls, 4 models |
| &bull; `gemini-flash-medium` | 75% | 20 calls |
| &bull; `deepseek-v4-pro` | 70% | 20 calls |
| &bull; `deepseek-v4-flash` | 45% | 20 calls |
| &bull; `deepseek-v4.1-flash` | 25% | 20 calls |
| **Trap Effectiveness: `fictional_term`** | **100%** (10 comply / 0 pushback) | n = 12 valid calls |
| **Trap Effectiveness: `trap_number`** | **58%** | n = 48 calls |
| **Verifier Model Catch Rate** | **65%** | 13 of 20 hallucinations caught |
| **JSON Schema Structured Output Validity** | **100%** | 4 of 4 schema calls |

To execute the benchmark suite:
```bash
python eval/run_benchmarks.py
```

---

## 8. License & Event Compliance

- **Event:** AI Builder Cup 2026 (Google Cloud x Hack2skill)
- **Track Alignment:** Track 4 (Media, Content & Digital Experiences — Adaptive Learning)
- **Model Compliance:** Powered strictly by **Google Gemini** models via the official Google Gen AI SDK.
- **License:** Apache-2.0
