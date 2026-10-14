"""Deterministic honeypot catalog + classifier (ADR 002, ADR 005).

The catalog lives in ``prompts/honeypot-catalog.json`` so every injection is
auditable and repeatable. ``classify_honeypot`` maps a student's stance to one of
four fixed classes; the class -> points mapping is frozen in code, never generated
by the model (ADR 002 section 2.3).
"""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
CATALOG_PATH = _REPO / "prompts" / "honeypot-catalog.json"

# Frozen class -> points mapping (ADR 002 section 2.3). Never derive points from a model.
CLASS_POINTS = {
    "CRITICAL_REJECTION": 2,
    "AI_HALLUCINATION_COPYPASTE": -2,
    "UNVERIFIED_HONEST": 0,
    "EVASIVE": -1,
}

_cache: list[dict] | None = None

# Rejection indicators: the student questioned the premise or named it fictitious.
_REJECTION = (
    "does not exist", "doesn't exist", "not a real", "not a concept", "fictional",
    "no such thing", "never heard", "not in react docs", "not official", "made up",
    "hallucination", "fake", "tidak ada", "bukan konsep resmi", "bukan istilah",
    "tidak dikenal", "tidak pernah mendengar", "tidak pernah dengar", "bukan bagian",
    "salah premis", "tidak resmi", "buatan", "fiktif", "tidak valid",
)
# Honest ignorance: neutral, must NOT be punished (ADR 002 risk R7).
_HONEST = (
    "saya tidak tahu", "gw gak tau", "gw tidak tahu", "aku tidak tahu", "i don't know",
    "i do not know", "kurang tahu", "belum pernah baca", "not familiar", "belum pernah dengar",
    "unsure", "i am not sure", "i'm not sure", "tidak yakin", "gak tau",
)


def load_catalog() -> list[dict]:
    """All catalog entries (cached after first read)."""
    global _cache
    if _cache is None:
        data = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
        terms = data.get("terms") if isinstance(data, dict) else data
        if not isinstance(terms, list) or not terms:
            raise ValueError(f"honeypot catalog has no terms: {CATALOG_PATH}")
        _cache = terms
    return _cache


def _topic_score(entry: dict, topic: str) -> int:
    topic_l = (topic or "").lower()
    if not topic_l:
        return 0
    score = sum(1 for kw in entry.get("topic_keywords", []) if kw.lower() in topic_l)
    if entry.get("category", "").split("/")[0].lower() in topic_l:
        score += 1
    return score


def pick_honeypot_term(chapter_topic: str, used: set[str], *, seed: str | None = None) -> dict:
    """Pick a catalog term for a chapter topic, rotating away from ``used`` terms.

    Deterministic: ties break by ``catalog_id``. With ``seed`` set, a controlled
    variation (ADR 005 section 2) is chosen deterministically so a cached demo run and
    a live run resolve to the SAME surface form for the same chapter (ADR 005 section 3).
    """
    catalog = load_catalog()
    used = used or set()
    available = [e for e in catalog if e["term"] not in used]
    if not available:
        available = catalog  # whole catalog exhausted: rotate from the start

    def rank(entry: dict):
        return (-_topic_score(entry, chapter_topic), entry["catalog_id"])

    chosen = sorted(available, key=rank)[0]
    term = chosen["term"]
    variants = chosen.get("variants") or []
    if seed and variants:
        h = int(hashlib.sha1(f"{seed}|{term}".encode("utf-8")).hexdigest(), 16)
        term = variants[h % len(variants)]
    return {
        "term": term,
        "catalog_id": chosen["catalog_id"],
        "category": chosen["category"],
        "source": "deterministic_catalog",
        "expected_action": chosen.get("expected_action", "REJECT_AS_FICTITIOUS"),
    }


def classify_honeypot(user_response: str, term: str) -> dict:
    """Classify a student response about ``term`` into one of four fixed classes.

    Returns ``{result, points, analysis}``. Order matters: explicit rejection beats
    honest-ignorance wording; an elaborate answer that validates the fake term is
    copypaste; everything else is evasive.
    """
    res = (user_response or "").lower()
    term_l = (term or "").lower()

    if any(kw in res for kw in _REJECTION):
        result = "CRITICAL_REJECTION"
        analysis = f"Student identified and critically rejected the fictitious premise '{term}'."
    elif any(kw in res for kw in _HONEST):
        result = "UNVERIFIED_HONEST"
        analysis = f"Student transparently acknowledged unfamiliarity with '{term}' (neutral, not penalised)."
    elif len(res.split()) > 10 and term_l in res:
        result = "AI_HALLUCINATION_COPYPASTE"
        analysis = (
            f"Student gave an elaborate explanation validating the synthetic concept '{term}' — "
            "characteristic of external-LLM copypaste."
        )
    else:
        result = "EVASIVE"
        analysis = f"Student response skirted around '{term}' without resolving the premise."

    return {"result": result, "points": CLASS_POINTS[result], "analysis": analysis}
