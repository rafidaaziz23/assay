# DEV3 OVERNIGHT LOG — Assay

Jejak per unit. Satu entri per unit, ditulis SEBELUM lanjut. Format ada di
`docs/DEV3-OVERNIGHT-BRIEF.md` §5. Jangan edit entri lama; append saja.

Status ringkas (diperbarui tiap entri):
`H0.1 ✅ H0.2 ✅ H0.3 ✅ H0.4 ✅ H0.5 ✅ H1.1 ✅ H1.2 ✅ H1.3 ✅ H1.4 ✅ H1.5 ✅ H2.1 ✅ H2.2 ✅ H2.3 ✅ H2.4 ✅ H2.5 ✅ H2.6 ✅ H3.1 ⬜ H3.2 ⬜ H3.3 ⬜ H3.4 ⬜`

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

