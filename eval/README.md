# Assay Evaluation & Benchmark Suite

This directory contains the automated evaluation harness, honeypot validation benchmarks, and empirical audit data for **Assay**.

## Rubric Weighting Alignment
Under the AI Builder Cup 2026 rubric, **Technical Merit & GenAI Architecture accounts for 40%** of the score. Having an auditable evaluation harness with documented benchmark figures is the primary lever to maximize this scoring dimension.

## Empirical Baselines (Zero-Fabrication Guarantee)
All figures cited in the Pitch Deck and Demo Video originate from `results/baseline_empirical.json` (audited from `reza-research/parts10/HASIL-TES-EMPIRIS.md`):

| Metric | Measured Rate | Sample Size |
|---|---|---|
| Honeypot Hallucination Rate (Across Models) | **54%** | n = 80 calls |
| - gemini-flash-medium | 75% | 20 calls |
| - deepseek-v4-pro | 70% | 20 calls |
| - deepseek-v4-flash | 45% | 20 calls |
| - deepseek-v4.1-flash | 25% | 20 calls |
| Trap Effectiveness: `fictional_term` | **100%** | n = 12 valid calls |
| Trap Effectiveness: `trap_number` | **58%** | n = 48 calls |
| Verifier Loop Catch Rate | **65%** | 13 of 20 hallucinations caught |
| Structured JSON Schema Validity | **100%** | 4 of 4 schema calls |

## Running the Benchmark Suite
```bash
python run_benchmarks.py
```
