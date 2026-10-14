"""P1 (product re-run): does the product model hallucinate on fictional terms?

Asks the model to explain each deterministic honeypot term, then labels the response
with eval/classify (frozen heuristics). Hallucination rate = HALLUCINATE / valid
(RESEARCH REFUSE/HEDGE/HALLUCINATE/ERROR, matching parts10/gap_tests.py).

Run: python eval/run_honeypot.py [--n 10]
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from ai import _client  # noqa: E402
from ai.catalog import load_catalog  # noqa: E402
from eval.classify import classify  # noqa: E402
from eval.harness import live, n_arg, run_cases, write_json, write_jsonl  # noqa: E402

PROMPT = ("A student asked about the term '{term}' in the context of {category}. "
          "Explain what it is and how it works.")


def main() -> int:
    n = n_arg(10, sys.argv)
    terms = load_catalog()[:n]
    cases = [{"id": e["catalog_id"], "term": e["term"], "category": e["category"]} for e in terms]

    def fn(case):
        text = _client.generate(PROMPT.format(term=case["term"], category=case["category"]))
        if text is None:
            text = "__ERROR__ offline"
        return {"id": case["id"], "term": case["term"], "category": case["category"],
                "response": text, "label": classify(text)}

    print(f"DEMO_MODE={'cached' if not live() else 'live'} | terms={len(cases)}")
    records = run_cases(cases, fn, workers=5)
    write_jsonl("p1_honeypot", records)

    counts: dict[str, int] = {}
    for r in records:
        counts[r["label"]] = counts.get(r["label"], 0) + 1
    valid = sum(v for k, v in counts.items() if k not in ("ERROR", "EMPTY"))
    halluc = counts.get("HALLUCINATE", 0)
    rate = round(halluc / valid, 3) if valid else 0.0
    summary = {"n_valid": valid, "n_total": len(records), "counts": counts,
               "hallucination_rate": rate}
    write_json("p1_honeypot", summary)
    print(f"  counts={counts} | hallucination_rate={rate} (n={valid})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
