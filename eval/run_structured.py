"""P5 (product re-run): native structured output validity (response_schema).

Sends N prompts with a strict JSON schema and counts how many replies parse and
validate. RESEARCH measured 4/4 (100%).

Run: python eval/run_structured.py [--n 4]
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from ai import _client  # noqa: E402
from eval.harness import live, n_arg, run_cases, write_json, write_jsonl  # noqa: E402
from eval.smoke_structured import SCHEMA, validate  # noqa: E402

PROMPTS = [
    "Evaluate: 'Chunking always improves retrieval accuracy.'",
    "Evaluate: 'A mutex guarantees zero latency.'",
    "Evaluate: 'TypeScript makes runtime type errors impossible.'",
    "Evaluate: '80% test coverage guarantees no production bugs.'",
]


def main() -> int:
    n = n_arg(len(PROMPTS), sys.argv)
    cases = [{"id": f"s{i:02d}", "prompt": p} for i, p in enumerate(PROMPTS[:n], 1)]

    def fn(case):
        out = _client.generate(
            "Reply ONLY with JSON matching the schema. " + case["prompt"], schema=SCHEMA)
        valid = False
        try:
            validate(out)
            valid = True
        except Exception:
            valid = False
        return {"id": case["id"], "prompt": case["prompt"], "valid": valid, "response": out}

    print(f"DEMO_MODE={'cached' if not live() else 'live'} | prompts={len(cases)}")
    records = run_cases(cases, fn, workers=2)
    write_jsonl("p5_structured", records)
    errors = sum(1 for r in records if r["response"] is None)
    returned = [r for r in records if r["response"] is not None]
    ok = sum(1 for r in returned if r["valid"])
    rate = round(ok / len(returned), 3) if returned else 0.0
    write_json("p5_structured", {"attempts": len(records), "errors": errors,
                                 "n": len(returned), "valid": ok, "validity_rate": rate})
    print(f"  valid={ok}/{len(returned)} (errors={errors}) | validity_rate={rate}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
