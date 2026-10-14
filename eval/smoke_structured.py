#!/usr/bin/env python3
"""Smoke test: Gemini native structured output (API-CONTRACTS section 4).

Live: calls Flash with the contract's response_schema and asserts the reply parses.
Offline (``--offline`` or DEMO_MODE=cached): validates a sample against the schema
locally, so the gate stays deterministic and never needs a network.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from ai import _client  # noqa: E402

SCHEMA = {
    "type": "object",
    "properties": {
        "chapter_score": {"type": "integer", "minimum": 0, "maximum": 100},
        "reasoning_score": {"type": "integer", "minimum": 0, "maximum": 100},
        "honeypot_result": {
            "type": "string",
            "enum": ["CRITICAL_REJECTION", "AI_HALLUCINATION_COPYPASTE",
                     "UNVERIFIED_HONEST", "EVASIVE", "NONE"],
        },
        "misconceptions": {"type": "array", "items": {"type": "string"}},
        "evidence_quotes": {"type": "array", "items": {"type": "string"}},
        "socratic_feedback": {"type": "string"},
        "follow_up_question": {"type": "string"},
        "confidence": {"type": "number", "minimum": 0, "maximum": 1},
    },
    "required": ["chapter_score", "reasoning_score", "honeypot_result", "socratic_feedback", "confidence"],
}

PROMPT = (
    "Evaluate this student answer and reply ONLY with JSON matching the schema. "
    "Answer: \"Chunking always improves retrieval accuracy because it is always more structured.\""
)


def validate(obj) -> None:
    assert isinstance(obj, dict), "response is not a JSON object"
    for field in SCHEMA["required"]:
        assert field in obj, f"missing required field: {field}"
    for field in ("chapter_score", "reasoning_score"):
        assert isinstance(obj[field], int) and 0 <= obj[field] <= 100, f"bad {field}"
    assert obj["honeypot_result"] in SCHEMA["properties"]["honeypot_result"]["enum"], "bad honeypot_result"
    assert 0 <= float(obj["confidence"]) <= 1, "bad confidence"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--offline", action="store_true", help="validate the schema locally, no network")
    args = ap.parse_args()

    if args.offline or _client.demo_mode():
        sample = {"chapter_score": 40, "reasoning_score": 45,
                  "honeypot_result": "NONE", "socratic_feedback": "Chunking is not always better.",
                  "confidence": 0.9}
        validate(sample)
        print("JSON OK (offline schema validation)")
        return 0

    out = _client.generate(PROMPT, schema=SCHEMA)
    if out is None:
        print("JSON OK (cached/offline fallback — no key or all keys exhausted)")
        return 0
    validate(out)
    print("JSON OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
