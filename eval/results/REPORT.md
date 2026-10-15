# Assay eval — product vs research baseline

| Metric | Product (this run) | Research baseline | n (product) |
|---|---|---|---|
| Honeypot hallucination rate | 87.5% | 54% | 8 |
| Trap: fictional_term | 100.0% | 100% | 2 |
| Trap: trap_number | 100.0% | 58% | 2 |
| Trap: false_premise | 50.0% | 25% | 2 |
| Trap: over_claim | 100.0% | 25% | 1 |
| Verifier catch rate | 6/6 (100.0%) | 13/20 (65%) | 6 |
| Structured output validity | 2/2 (100.0%) | 4/4 (100%) | 2 |
| RAG recall@3 | 0.909 | — | 22 |
| RAG page-hit@1 | 0.682 | — | 22 |
| RAG refusal accuracy | 100.0% | target 2/2 | 2 |

_All numbers come from eval/results/*.json or HASIL-TES-EMPIRIS.md. No rounding up. n is the valid sample per metric._
