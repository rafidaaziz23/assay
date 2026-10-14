"""Aggregate eval results into a markdown table, with n on every row.

Compares the product re-run against the research baseline in
`reza-research/parts10/HASIL-TES-EMPIRIS.md`. Every row carries its sample size `n` —
no number without `n` (DEV3-ROADMAP section 11). Numbers outside these two sources are
forbidden.

Run: python eval/report.py   ->  prints the table and writes eval/results/REPORT.md
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
RESULTS = REPO / "eval" / "results"

# Research baseline (HASIL-TES-EMPIRIS.md). Do not edit; product runs are compared to this.
RESEARCH = {
    "honeypot_rate": ("54%", 80),
    "fictional_term": ("100%", 12),
    "trap_number": ("58%", 48),
    "false_premise": ("25%", 48),
    "over_claim": ("25%", 48),
    "verifier_catch": ("13/20 (65%)", 20),
    "structured_validity": ("4/4 (100%)", 4),
}


def _load(name: str):
    p = RESULTS / f"{name}.json"
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


def _pct(x: float) -> str:
    return f"{round(100 * x, 1)}%"


def build() -> str:
    lines = ["# Assay eval — product vs research baseline", ""]
    lines.append("| Metric | Product (this run) | Research baseline | n (product) |")
    lines.append("|---|---|---|---|")

    p1 = _load("p1_honeypot")
    if p1:
        lines.append(f"| Honeypot hallucination rate | {_pct(p1['hallucination_rate'])} | "
                     f"{RESEARCH['honeypot_rate'][0]} | {p1['n_valid']} |")

    p2 = _load("p2_traps")
    if p2:
        for trap in ("fictional_term", "trap_number", "false_premise", "over_claim"):
            if trap in p2:
                b = p2[trap]
                n = b["comply"] + b["pushback"]
                r = RESEARCH.get(trap, ("—", "—"))
                lines.append(f"| Trap: {trap} | {_pct(b['effectiveness'])} | {r[0]} | {n} |")

    p4 = _load("p4_verifier")
    if p4:
        lines.append(f"| Verifier catch rate | {p4['caught']}/{p4['n']} ({_pct(p4['catch_rate'])}) | "
                     f"{RESEARCH['verifier_catch'][0]} | {p4['n']} |")

    p5 = _load("p5_structured")
    if p5:
        lines.append(f"| Structured output validity | {p5['valid']}/{p5['n']} ({_pct(p5['validity_rate'])}) | "
                     f"{RESEARCH['structured_validity'][0]} | {p5['n']} |")
    rag = _load("rag_metrics")
    if rag:
        lines.append(f"| RAG recall@3 | {rag['recall_at_3']} | — | {rag['answerable_questions']} |")
        lines.append(f"| RAG page-hit@1 | {rag['page_hit_rate_at_1']} | — | {rag['answerable_questions']} |")
        lines.append(f"| RAG refusal accuracy | {_pct(rag['refusal_accuracy'])} | target 2/2 | {rag['unanswerable_questions']} |")

    lines.append("")
    lines.append("_All numbers come from eval/results/*.json or HASIL-TES-EMPIRIS.md. "
                 "No rounding up. n is the valid sample per metric._")
    return "\n".join(lines)


def main() -> int:
    table = build()
    print(table)
    (RESULTS / "REPORT.md").write_text(table + "\n", encoding="utf-8")
    print(f"\nwrote {RESULTS / 'REPORT.md'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
