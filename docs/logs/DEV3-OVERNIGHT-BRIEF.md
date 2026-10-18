# DEV3 OVERNIGHT BRIEF — Assay (AI Engine & Eval)

Working contract for an unattended overnight run. Read it **at the start of every run**, not once.
If this brief and your memory/guess disagree, **the brief wins**.

- **Repo:** `D:/Project/assay` (the product repo; `ai-builder-cup-research` only holds the spec)
- **Plan source:** `D:/Project/ai-builder-cup-research/active-learning-engine/DEV3-ROADMAP.md`
- **Document authority:** `DEV3-ROADMAP.md` §1 → `docs/architecture/API-CONTRACTS.md` (LOCKED) → `docs/product/PRD.md`
  → ADRs `docs/adrs/001..005`. On conflict: **API-CONTRACTS wins**.
- **Gate:** `tools\gate-dev3.cmd` (mandatory; exit 0 = green)
- **Trace:** `docs/logs/DEV3-OVERNIGHT-LOG.md` — one entry per unit, written BEFORE moving on
- **Start:** evening of 2026-10-14

## 0a. Work mode & run decisions (from Reza)

- **This is a `/goal` loop.** At the end of every turn the judge checks the goal. If it is not done, you continue automatically.
  **Do not stop and ask** — work the next unit until the budget runs out or the goal is `done`.
- **Tonight's scope:** Days 0–2 (H0.x, H1.x, H2.x). Day 3 (H3.x) **only if** every H0–H2 unit is
  `DONE` and there is still time. Do not start H3 before H0–H2 are finished.
- **Commit locally, do not push.** Commit messages + code comments **must be in English** (commit
  `feat(ai): ...`; code comments in English). Log/brief prose is in English too.
- **API key = FRUGAL.** Live calls only for 1–2 pieces of evidence per unit (the ones that genuinely need the model). Everything else
  offline/cached. Three keys in `.env`, rotation order: `GOOGLE_API_KEY` → `GOOGLE_API_KEY_FALLBACK`
  → `GOOGLE_API_KEY_FALLBACK_2`. If a key returns `429`/`RESOURCE_EXHAUSTED`, switch to the
  next key immediately; if all three are exhausted, mark the unit that needs live calls as `BLOCKED (quota)` and
  continue with offline units.
- **Safety net:** the `assay-dev3-watchdog` cron sends a log summary to Telegram every 15 minutes
  if something changed. If you see a STUCK message, write it in the log and try to continue.

---

## 0. Hard rules (a violation = failed run)

1. **Write ONLY in:** `ai/`, `prompts/`, `eval/`, `tools/gate-dev3.cmd`, `docs/logs/DEV3-*.md`,
   `ai/MODELS.md`, `ai/FIXTURES.md`. **DO NOT touch** `frontend/`, `backend/`, other `docs/*`,
   `.gitignore`, `package.json`, `README.md`. Those belong to DEV 1 / DEV 2.
2. **Google-only in the product runtime.** Only the `google-genai` SDK. Zero other providers in `ai/` or `backend/`.
3. **Zero secrets in committable files.** API keys live in `D:/Project/assay/.env` (gitignored).
   Read from there; never print the values; never write them into the brief/log/commits. Zero chat IDs / tokens in the repo.
4. **Zero invented numbers.** Any number may only come from `eval/results/` or
   `ai-builder-cup-research/reza-research/parts10/HASIL-TES-EMPIRIS.md`. Inventing new numbers is forbidden.
5. **Local commit per unit, DO NOT push.** The remote is the team repo. `git add <unit files>` only,
   conventional message (`feat(ai): ...` / `test(eval): ...`). No blind `git add -A`, no `--force`.
6. **Never ask a human, never wait for approval.** If stuck: record the blocker in the log,
   mark the unit `BLOCKED`, and continue with the next unit that can still be done.
7. **Pure functions.** Everything in `ai/` does no network I/O except model calls. Easy to test.
8. **A green gate is a requirement**, not a bonus. A unit may only be marked `DONE` after the gate is green.

## 1. Per-run setup (5 seconds)

```bash
cd /d/Project/assay
PY=.venv/Scripts/python.exe
[ -x "$PY" ] || echo "VENV MISSING — see unit H0.1"
```

If `.venv` does not exist: do **H0.1** first (create the venv + install), it is a prerequisite for every unit.

## 2. How to pick a unit

1. Read `docs/logs/DEV3-OVERNIGHT-LOG.md` — find the first unit that is **not** `DONE`.
2. Finish **that ONE unit** plus a green gate. Do not work two units at once.
3. If the unit is large (e.g. H0.3), it may take the whole run; do not move on before `DONE`.
4. Write the log entry (format §5), commit locally, then **end the run** with the 3-line status (§6).

## 3. Unit list (in order; work from the top)

Every unit has an **action**, **artifacts**, and **"DONE when"** (concrete verification). Taken from
`DEV3-ROADMAP.md` §2–§5; summarized below so a run does not have to re-read them every time
(read the roadmap when you need detail).

### DAY 0 — setup & baseline
| ID | Action | DONE when |
|---|---|---|
| H0.1 | `.venv` (python 3.11/3.12) + install `google-genai pytest pytest-asyncio python-dotenv pymupdf reportlab pypdf`. Write `ai/MODELS.md` (exact model IDs + align with ADR 001). | `.venv/Scripts/python.exe -c "import google.genai, fitz, pytest"` succeeds; `ai/MODELS.md` exists |
| H0.2 | `eval/smoke_structured.py`: call Flash with the `response_schema` from API-CONTRACTS §4, parse the JSON. `--offline` mode = local schema validation (zero network). | `python eval/smoke_structured.py` prints `JSON OK` without an exception |
| H0.3 | Stub ALL functions from `DEV3-ROADMAP §1` in `ai/__init__.py` (return static fixtures in the API-CONTRACTS shape) + `ai/FIXTURES.md` (sample output per function). | `python -c "import ai; ai.classify_intent('x')"` returns a dict with the right shape; FIXTURES.md exists |
| H0.4 | `eval/classify.py`: port the regex logic from `reza-research/parts10/honeypot_test.py` (REFUSE/HEDGE/HALLUCINATE/ERROR). **Do not change the label definitions** (so results stay comparable to the n=80 baseline). | a `classify(text)` function exists; the small unit test is green |
| H0.5 | `prompts/honeypot-catalog.json`: 10 fictional terms mapped to topics (ADR 005). Terms may come from the `honeypot_test.py` TERMS + those already in `backend/app/services/honeypot_catalog.py` (do not modify that backend file). | valid JSON file, 10 entries, each entry has `term`+`category`+`trap_type`+`expected_action` |

### DAY 1 — intake → checklist → syllabus
| ID | Action | DONE when |
|---|---|---|
| H1.1 | `ai.classify_intent` (ADR 004): intent → `role_guess` from the 9 seeds + `suggested_others`. | 10 test intents (5 seed, 5 odd) → correct `suggested_others` ≥ 9/10; write `eval/results/intent_cases.jsonl` |
| H1.2 | `ai.gen_checklist`: items + `origin` (`document`/`role_taxonomy`/`grounded_external`) + `confidence`. | 1 intent + 1 PDF → ≥ 3 items, every item has a valid `origin` |
| H1.3 | `ai.index_document`: text extraction + **page numbers** (page-anchored, PyMuPDF). | sample PDF → every chunk has a `page`; total pages match the real PDF |
| H1.4 | `ai.synth_syllabus`: chapter `title/order/objectives/estimated_reading_minutes/source_pages`. No-PDF path → `source_mode: role_taxonomy_generated`. | 2 runs (with & without PDF) → ≥ 3 chapters, `source_pages` present on the PDF path, correct `source_mode` |
| H1.5 | External grounding via Google Search for **1 chapter only**, results `cached: true`. | `references[]` has 1 `grounded_external` with `cached: true`; cut the network → falls back to cache, zero exceptions |

### DAY 2 — reader ask + interview + honeypot
| ID | Action | DONE when |
|---|---|---|
| H2.1 | `ai.socratic_ask`: answers with a question/hint, does **not** answer directly. | 10 test questions → `gave_direct_answer == False` in 10/10 |
| H2.2 | `ai.suggest_questions`: multi-word selection → 3 relevant, non-duplicate questions. | selection "reconciliation and diffing" → 3 unique questions |
| H2.3 | Multi-turn interview prompt (2–3 rounds, HOTS + adaptive follow-up), keep history, `running_score` rises. | `start_interview`/`interview_turn` return the §2.5 shape |
| H2.4 | `ai.pick_honeypot_term` (catalog lookup + ADR 005 variation, rotate per session) + `ai.classify_honeypot` (4 classes → fixed points). | Case A copy-paste → `AI_HALLUCINATION_COPYPASTE` −2; Case B rejection → `CRITICAL_REJECTION` +2; Case C "don't know" → `UNVERIFIED_HONEST` 0 |
| H2.5 | `ai.score_chapter`: `clamp(reasoning_score + honeypot_points + integrity_adjustment, 0, 100)`; `integrity_adjustment = {clean:0, assisted:-3, assisted_unverified:0}`. Record this decision as a `# ponytail:` comment in the code. | case table (80/−2/assisted) → results match the formula |
| H2.6 | `ai.verify_score`: second model (Pro) → `status: agreed|uncertain` + note. | 5 test scores → all return a valid `status`, zero exceptions |

### DAY 3 — stretch (only if H0–H2 are all DONE and there is still time)
| ID | Action | DONE when |
|---|---|---|
| H3.1 | `ai.calibration_label`: `overconfident` (pred > actual+15), `underconfident` (pred < actual−15), `well_calibrated`. | 3 boundary cases (gap 20/−20/5) get the right label |
| H3.2 | Appeal handler stub: `{appeal_id, status:"under_review", reviewer:"verifier_model", possible_outcome:[...]}`. | returns the §2.8 shape |
| H3.3 | `eval/harness.py` (threaded caller, workers=5) + `run_honeypot.py`, `run_traps.py`, `run_verifier.py`, `run_structured.py` + `eval/report.py` → markdown table. Runs **against the product's Google models** (Flash/Pro). | `python eval/report.py` → table is produced, every row has `n`, zero numbers without `n` |
| H3.4 | Lock the numbers: compare the product against the research baseline, record why if they differ. Put the final table in the log. | final table in `eval/results/` + the log |

## 4. Gate

```cmd
tools\gate-dev3.cmd
```
Green = exit 0. It checks (offline, < 300s): `import ai` + `pytest eval/tests -q` (if present)
+ validation of `prompts/honeypot-catalog.json`. If red: read the output, fix it, re-run.
**Max 3 attempts per unit.** If it is still red → mark the unit `BLOCKED`, write it up as-is in the log, move on.

This gate is **offline** — it does not exercise model calls. If a unit needs live evidence (grounding, verdict),
run its verification script manually and **paste the raw output into the log**. Never claim "live OK" without output.

## 5. Log entry format (append to `docs/logs/DEV3-OVERNIGHT-LOG.md`)

```
### <ID> — <title> — <DONE|BLOCKED|PARTIAL> — <YYYY-MM-DD HH:MM WIB>
- Action: <1-2 lines>
- Artifacts: <files created/changed>
- Evidence: <command + short raw result (gate output / live verification)>
- Notes: <decisions, contract conflicts, risks>
```

## 6. End-of-run status (MANDATORY, it becomes the Telegram message)

End every run with EXACTLY 3 lines, short:

```
[DEV3] unit=<ID> status=<DONE|BLOCKED|PARTIAL> gate=<GREEN|RED>
remaining: <n units not DONE> — next <ID>
<1 line if there is a blocker/key decision, otherwise write "ok">
```
(`gate=` reports the gate's own verdict; the gate tool prints `GATE HIJAU` / `GATE MERAH`, i.e. green / red.)

## 7. When to stop (stop condition)

- **H0–H2 green ≠ done.** Do not stop after H0–H2. Continue to H3 (H3.1–H3.4) while there is still budget.
- **Bounded.** Stop starting new units at **07:00 WIB**. If that time has not passed and units remain: continue.
- If every H0–H3 unit is `DONE` → write the closing summary in the log, then **pause the job yourself**:
  ```bash
  hermes cron list            # find the 'assay-dev3' job id
  hermes cron pause <id>
  ```
  and end the run with `[DEV3] DONE — all units complete`.
- If a unit is `BLOCKED` and no other unit can be worked → write the closing summary + pause the job.
- If the gate is red 3× on the same unit → `BLOCKED`, move to another unit (do not stop entirely).

## 8. Not guaranteed / out of scope

- `frontend/` and `backend/` (DEV 1 / DEV 2). If you need a new endpoint → note it in the log, do not build it.
- Pushing to the remote (team repo). Local commits only.
- Video/deck/pitch. That is DEV 1.
- New numbers outside `eval/results/` and `HASIL-TES-EMPIRIS.md`.
