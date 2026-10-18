# Assay Evaluation Suite

Two different things live here, and conflating them is how benchmark numbers
become fiction. They are labelled separately on purpose.

| Artifact | What it actually is | Reproducible from this repo? |
|---|---|---|
| `run_benchmarks.py` | **Unit test** of the deterministic classifier | Yes — 4/4, no network |
| `results/*.jsonl` | **Captured model responses**, 28 records total | Partly — responses are stored, provenance is not |
| `results/baseline_empirical.json` | **External audit**, n=80 across 4 models | **No** — source is outside this repo |

## 1. What runs here, offline

```bash
python run_benchmarks.py
```

```
[PASS] Test Case 1: Term='React Quantum Hook' -> AI_HALLUCINATION_COPYPASTE (score=-2)
[PASS] Test Case 2: Term='React Quantum Hook' -> CRITICAL_REJECTION (score=2)
[PASS] Test Case 3: Term='Zero-Latency Mutex'  -> UNVERIFIED_HONEST (score=0)
[PASS] Test Case 4: Term='bcSQL indexing'      -> EVASIVE (score=-1)
Honeypot Classification Accuracy: 4/4 (100.0%)
```

**This makes no model calls.** It feeds four hardcoded strings to
`classify_honeypot_response()` and checks the label. It proves the classifier is
deterministic and correctly wired. It says nothing about how any LLM behaves.

Read it as a unit test, not as a benchmark.

## 2. What is stored in `results/`

| File | Records | Labels |
|---|---|---|
| `p1_honeypot.jsonl` | 10 | 7 HALLUCINATE, 1 REFUSE, 2 ERROR |
| `p2_traps.jsonl` | 8 | 6 COMPLY, 1 PUSHBACK, 1 ERROR |
| `p4_verifier.jsonl` | 6 | verifier judgements |
| `p5_structured.jsonl` | 4 | schema validity |
| `intent_cases.jsonl` | 10 | intent classification cases |

These are real captured responses — the text in `p1_honeypot.jsonl` is what models
actually returned when asked about fabricated concepts.

**Limitation, stated plainly:** the records carry no `model` field. Per-model
attribution cannot be reconstructed from the stored data alone.

## 3. The external audit (n=80)

`results/baseline_empirical.json` records an audit dated **2026-10-14**, sourced
from `reza-research/parts10/HASIL-TES-EMPIRIS.md` — **a document outside this
repository**.

| Metric | Rate | Sample |
|---|---|---|
| Honeypot hallucination, all models | 54% | n = 80 |
| · `gemini-flash-medium` | 75% | 20 |
| · `deepseek-v4-pro` | 70% | 20 |
| · `deepseek-v4-flash` | 45% | 20 |
| · `deepseek-v4.1-flash` | 25% | 20 |
| Trap `fictional_term` | 100% | 12 (10 comply, 0 pushback, 2 error) |
| Trap `trap_number` | 58% | 48 |
| Trap `false_premise` | 25% | 48 |
| Verifier catch rate | 65% | 13 of 20 |
| Structured JSON validity | 100% | 4 |

**You cannot regenerate this table from the repo.** The raw 80-call dataset is not
committed. Treat it as a cited external result, not as evidence a reader can verify
by running a command.

### On the non-Google models in this table

The competition requires the **product** to be built on Google AI models. It does
not forbid measuring other models. These rows are adversarial baselines: they show
that competitor LLMs confidently explain concepts that do not exist, which is the
premise the honeypot depends on.

No non-Google model is called anywhere in `backend/`, `ai/`, `frontend/` or
`prompts/`. Verified by grep; the product path is Gemini only.

## 4. Reproducing the audit properly

Not done yet. To make §3 verifiable, the harness would need to:

1. call each model through its own API and record `model`, `term`, `response`, `label`;
2. commit the raw JSONL with the model field;
3. compute the rates from that file rather than from a hand-written summary.

Until then, the honest claim is: **28 captured responses in-repo, plus one cited
80-call external audit.** Not "80 calls you can re-run".
