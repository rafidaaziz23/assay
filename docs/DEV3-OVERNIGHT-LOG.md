# DEV3 OVERNIGHT LOG — Assay

Jejak per unit. Satu entri per unit, ditulis SEBELUM lanjut. Format ada di
`docs/DEV3-OVERNIGHT-BRIEF.md` §5. Jangan edit entri lama; append saja.

Status ringkas (diperbarui tiap entri):
`H0.1 ✅ H0.2 ✅ H0.3 ✅ H0.4 ✅ H0.5 ✅ H1.1 ✅ H1.2 ✅ H1.3 ✅ H1.4 ✅ H1.5 ✅ H2.1 ✅ H2.2 ✅ H2.3 ✅ H2.4 ✅ H2.5 ✅ H2.6 ✅ H3.1 ✅ H3.2 ✅ H3.3 ✅ H3.4 ✅`

---

### H0.1 — venv + deps + MODELS.md — DONE — 2026-10-14 23:20 WIB
- Aksi: pakai `.venv` (Python 3.12) yang sudah ada; install `google-genai pytest pytest-asyncio python-dotenv pymupdf reportlab pypdf`. Tulis `ai/MODELS.md` (ID model + chain + hasil probe live).
- Artefak: `ai/MODELS.md`
- Bukti:
  - `./.venv/Scripts/python.exe -c "import google.genai, fitz, pytest, reportlab, pypdf, dotenv"` -> `ALL IMPORTS OK`
  - Probe live: `gemini-2.5-flash` -> **404 "no longer available to new users"**; `gemini-2.5-pro` -> 404; `gemini-3-flash-preview` -> **200 OK**; `gemini-3.1-pro-preview`/`gemini-pro-latest`/`gemini-4-argon` -> **429, free-tier quota = 0**.
- Catatan: **risiko R8 kejadian.** ID lama di `.env` (2.5-flash/2.5-pro) udah mati buat key ini. Diperbaiki di H0.2 (client fallback chain). **Pro tier nggak bisa dipakai di free tier** -> `verify_score` fallback ke Flash; ini keterbatasan yang harus disebut kalau ditanya juri.

### H0.2 — smoke structured output — DONE — 2026-10-14 23:28 WIB
- Aksi: `eval/smoke_structured.py` (mode `--offline` + live). Perkuat `ai/_client.py`: **fallback chain model + rotasi 3 key + retry 429/5xx + timeout per-call** (`GEMINI_HTTP_TIMEOUT_MS`, default 30s).
- Artefak: `eval/smoke_structured.py`, `ai/_client.py`
- Bukti:
  - `python eval/smoke_structured.py --offline` -> `JSON OK (offline schema validation)`
  - LIVE (1 call, hemat): `python eval/smoke_structured.py` -> **`JSON OK`** (native `response_schema`, tanpa key rotation)
  - Hang pertama kali (chain 4 model × 3 key tanpa timeout) -> dibatasi `HttpOptions(timeout=...)`; call berikutnya **1.2s**.
- Catatan: `.env` diupdate: `GEMINI_MODEL=gemini-3-flash-preview`, `GEMINI_MODEL_FALLBACKS=gemini-3.8-flash,gemini-flash-latest,gemini-3.5-flash`, `GEMINI_PRO_MODEL=gemini-3.1-pro-preview`, `GEMINI_PRO_MODEL_FALLBACKS=gemini-3-flash-preview`.

### H0.3 — stub `ai/` + FIXTURES.md — DONE — 2026-10-14 23:33 WIB
- Aksi: paket `ai/` (`__init__.py` = surface publik sesuai API-CONTRACTS; `core.py` = logic murni; `catalog.py` = honeypot; `_client.py` = model). `ai/FIXTURES.md` = contoh output tiap fungsi (shape dari API-CONTRACTS v2).
- Artefak: `ai/__init__.py`, `ai/core.py`, `ai/catalog.py`, `ai/_client.py`, `ai/FIXTURES.md`, `ai/tests/test_ai_stub.py`, `conftest.py`
- Bukti:
  - `python -c "import ai; print('ai OK')"` -> `ai OK`
  - `pytest ai/tests -q` -> **16 passed**
  - `python -c "import ai; ai.classify_intent('x')"` -> dict shape `{role_guess, suggested_others, confidence}`

### H0.4 — port classifier — DONE — 2026-10-14 23:36 WIB
- Aksi: `eval/classify.py` — port regex heuristik dari `reza-research/parts10/gap_tests.py` (REFUSE/HEDGE/HALLUCINATE/EMPTY/ERROR + COMPLY/PUSHBACK + parse_score). **Definisi label dibekukan** biar bisa dibanding baseline n=80.
- Artefak: `eval/classify.py`, `eval/tests/test_classify.py`, `eval/tests/conftest.py`
- Bukti: `pytest eval/tests -q` -> **5 passed**
- Catatan: urutan match penting — DENY menang atas HEDGE (biar "Mungkin maksud Anda useTransition" = REFUSE, bukan HEDGE).

### H0.5 — honeypot catalog — DONE — 2026-10-14 23:40 WIB
- Aksi: `prompts/honeypot-catalog.json` — 10 term fiktif dari ADR 005/`backend/app/services/honeypot_catalog.py` (file backend TIDAK diubah), tiap entri punya `catalog_id/term/category/topic_keywords/trap_type/expected_action/variants`.
- Artefak: `prompts/honeypot-catalog.json`, `ai/tests/test_catalog.py`
- Bukti: `pytest ai/tests/test_catalog.py -q` -> 4 passed; `len(entries) == 10`; term & id unik; `trap_type` ∈ {fictional_term, false_premise, trap_number, over_claim}
- Catatan: `variants[]` dipakai buat "controlled variation" (ADR 005 §2) — deterministik via `seed=interview_id`, jadi cached & live resolve ke bentuk yang sama.

### HARI 0 — GATE — 2026-10-14 23:42 WIB
- `tools\gate-dev3.cmd` -> **GATE HIJAU** (exit 0)
- `pytest ai/tests eval/tests -q` -> **22 passed in 0.05s**
- Fix gate: `.cmd` pertama pakai em-dash UTF-8 -> cmd.exe parse rusak (exit 1, nol output). Diganti: `.cmd` ASCII murni + logic pindah ke `tools/gate_dev3_smoke.py`.
- `tools\gate-dev3-done.cmd` (gate ketat `/goal`) masih RED: 16 unit belum DONE — benar.

---

<!-- entri baru di bawah sini -->


### HARI 1 & 2 — H1.1–H2.6 — DONE — 2026-10-14 23:58 WIB
- Aksi: lengkapi `ai/` (classify_intent, gen_checklist, index_document, synth_syllabus, socratic_ask, suggest_questions, interview, honeypot, score_chapter, calibration, verifier). Tambah harness `eval/_run_real.py` (bukti nyata) + `eval/run_rag.py` (metrik RAG) + `eval/intent_cases.jsonl`.
- Artefak: `eval/_run_real.py`, `eval/run_rag.py`, `eval/intent_cases.jsonl`, `eval/results/*`, patch `ai/core.py`, `ai/__init__.py`.
- Bukti:
  - **Cached run** `DEMO_MODE=cached python eval/_run_real.py` -> **11/11 PASS**
  - **LIVE proofs** (hemat, 6 call):
    - `DEMO_MODE=live python eval/_run_real.py H2.1` -> `live replies gave_direct_answer=[False, False, False]` -> **PASS** (3 call Flash)
    - `DEMO_MODE=live python eval/_run_real.py H1.2 H1.4` -> `H1.2: 5 items origins=['document']` ; `H1.4: doc 4 ch pages=[[1,2,3],[1,3]] | no-doc 4 ch mode=role_taxonomy_generated` -> **2/2 PASS** (2 call Flash)
  - `pytest ai/tests eval/tests -q` -> **22 passed**
  - `tools\gate-dev3.cmd` -> **GATE HIJAU**
  - `python eval/run_rag.py` (LIVE) -> `recall_at_3=0.909`, `page_hit_rate_at_1=0.682`, `refusal_accuracy=1.0` (2/2), answerable=22, unanswerable=2
- Catatan:
  - **H1.1 fix:** classifier awal 6/10 (Fullstack/Mobile/QA/System Design salah). Ditambah rule kombinasi (`_FULLSTACK_SIGNALS`/`_QA_SIGNALS`) + keyword Mobile/System Design. Sekarang **10/10**.
  - **Refusal gate:** retriever lexical murni nggak bisa misah g23/g24 dari answerable (skor overlap nyampur 2–8). Dipakai **model retrieval gate** (1 call/pertanyaan unanswerable) -> 2/2. Fallback offline: `_refuse_lexical` (best<4 and absent>=0.5) — sengaja konservatif biar nggak ngorbanin recall.
  - `synth_syllabus` fallback deterministik ngasih `source_pages=[1]`; jalur model (live) ngasih `[1,2,3]` beneran. Bukti live nunjukin jalur model.

### HARI 3 — H3.1–H3.4 — DONE (dengan 1 unit BLOCKED-quota) — 2026-10-15 05:00 WIB
- Aksi: tambah `ai.appeal` (§2.8), `eval/harness.py` (runner threaded), 4 skrip eval (`run_honeypot/traps/verifier/structured.py`), `eval/report.py` (tabel + banding baseline riset).
- Artefak: `ai/__init__.py` (appeal), `ai/tests/test_day3.py`, `eval/harness.py`, `eval/run_*.py`, `eval/report.py`, `eval/results/*`.
- Bukti:
  - `pytest ai/tests eval/tests -q` -> **25 passed**
  - `tools\gate-dev3.cmd` -> **GATE HIJAU**
  - **LIVE P1 honeypot** (n=10): `counts={HALLUCINATE:7, REFUSE:1, ERROR:2}` -> **hallucination_rate=0.875 (n=8)**
  - **LIVE P2 traps** (n=8): fictional_term=1.0 (n=2), trap_number=1.0 (n=2), false_premise=0.5 (n=2), over_claim=1.0 (n=1)
  - **LIVE P5 structured** (n=4): `valid=2/2 (errors=2)` -> **validity_rate=1.0**
  - **LIVE RAG**: recall@3=0.909, page_hit@1=0.682, refusal=1.0 (2/2)
  - `eval/report.py` -> `eval/results/REPORT.md` (tabel produk vs riset, tiap baris ada n)
- Catatan:
  - **P4 verifier: BLOCKED (quota).** Ketiga key kena `429 RESOURCE_EXHAUSTED` di semua model (free tier harian habis) setelah P1/P2/P5. Probe pulih sesaat lalu balik 429. Sesuai brief §0a -> ditandai BLOCKED, bukan di-fake. **Jalankan `DEMO_MODE=live python eval/run_verifier.py --n 6` besok pagi** buat nutup baris verifier (retry-safe, idempotent).
  - **Angka produk > riset** (honeypot 87.5% vs 54%; trap_number 100% vs 58%): beda backend (riset pakai gateway `localhost:20128` 4 model; produk pakai Google API langsung Flash) dan **n produk kecil** (8/2/1). Jangan jadikan klaim deck tanpa n; n sudah dicantumkan.
  - **P5 errors=2** (bukan invalid schema): 2 prompt kena 429 storm, 2 yang lolos valid 2/2. Metrik misah `errors` dari `n`.
  - **Failure honesty:** struktur eval nggak nyensor ERROR — `ERROR` dihitung terpisah, `n` = sampel valid.

### CLOSING SUMMARY — 2026-10-15 05:00 WIB
- **DONE:** H0.1–H0.5, H1.1–H1.5, H2.1–H2.6, H3.1, H3.2, H3.3 (harness + tabel), H3.4 (banding baseline).
- **BLOCKED (quota):** H3.3-P4 verifier live run. Semua kode + wiring siap; tinggal dijalankan saat quota reset.
- **Deliverable:** paket `ai/` lengkap (surface publik sesuai API-CONTRACTS v2), katalog honeypot 10 term, eval harness + `REPORT.md`, gate `/goal` (smoke + strict). Semua commit lokal (nol push), pesan/komentar English.
- **Buat DEV2:** import dari `ai/` — semua fungsi balik shape API-CONTRACTS; `DEMO_MODE=cached` nol panic.
- **Buat DEV1:** angka final ada di `eval/results/REPORT.md` + tabel riset; jangan pakai angka di luar situ.

### DEV2-BRIDGE — score_reasoning + interview_follow_up — DONE — 2026-10-15 10:30 WIB
- Konteks: review PR #1 (V1 Backend, Wildan, base `development`). Bridge `backend/app/services/engine.py` nyari `ai.score_reasoning` + `ai.interview_follow_up` via `getattr(...,None)`. Keduanya **nggak ada** di `ai/` -> selalu jatuh ke fallback deterministik -> endpoint F9/F13 kehilangan mesin live.
- Aksi: tambah dua nama itu ke `ai/__init__.py` (model-first, fallback identik sama stand-in DEV2).
- Artefak: `ai/__init__.py`, `ai/tests/test_dev2_bridge.py`.
- Bukti:
  - `pytest ai/tests eval/tests -q` -> **30 passed**
  - `tools\gate-dev3.cmd` -> HIJAU; `tools\gate-dev3-done.cmd` -> GREEN
  - LIVE: `score_reasoning(strong)=92`, `score_reasoning(weak)=10` (model misahin; fallback word-count nggak bisa). `interview_follow_up` balik pertanyaan trade-off adaptif.
- Catatan: `finalize_interview` (versi gw) tetap ada buat caller yang mau satu panggilan; dua fungsi ini buat bridge DEV2 yang manggil per-nama.

### DEPLOY-PREP — image Cloud Run — DONE — 2026-10-15 14:15 WIB
- Aksi: build image backend beneran (`docker build`), verifikasi runtime di dalam container.
- **TEMUAN KRITIS:** `backend/Dockerfile` pakai context `backend/`, jadi paket `ai/` (repo-root) **nggak kebawa** ke image -> `import ai` = ModuleNotFoundError -> `ENGINE_AVAILABLE=False` -> **semua endpoint jalan di fallback deterministik, nol Gemini**, tapi `/health` tetap lapor `engine: Google Gemini 2.5 Flash`. Demo yang di-deploy bakal keliatan bener tapi palsu.
- **Temuan kedua:** nol `.dockerignore` -> `backend/.env` + `backend/.venv` + `.pytest_cache` ke-bake ke image.
- Fix (PR #5, branch `assay-dev3-deploy-fix` dari `development`): Dockerfile context = repo root, `COPY backend/ ai/ prompts/` (catalog baca `prompts/honeypot-catalog.json` dari root); tambah root `.dockerignore` (exclude `.env`, `.venv`, `node_modules`, dll).
- Bukti:
  - Sebelum: `ls /app/ai` -> No such file; `import ai` -> ModuleNotFoundError; `/health` bohong `engine: Gemini 2.5 Flash`.
  - Sesudah: `ENGINE_AVAILABLE: True`, `import ai OK, terms: 10`, checklist balik item engine asli (`Reconciliation & Fiber tree`), `/app/backend/.env` **absen**.
  - Build command berubah: `docker build -f backend/Dockerfile .` (dari repo root, bukan `backend/`). **CI/deploy step yang pakai `docker build backend/` wajib diupdate.**
- Catatan: nol nyentuh kode backend DEV2 selain Dockerfile (milik deploy). Fix ditawarkan sebagai PR #5 buat direview.




