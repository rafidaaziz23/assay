"""Scoring integration (F9/F13).

DEV 3 owns the score formula (`ai/core.py:score_chapter`) and the honeypot classifier
(`ai/catalog.py`). DEV 2 owns the two inputs the engine cannot see — the integrity flag
produced by Focus Mode events, and the verifier's second opinion — plus the state
transition that consumes the result.

Two deliberate rules live here:

1. **Honeypot is a score dimension, never a gate.** The class maps to ±points and the
   unlock threshold stays on ``chapter_score`` (ADR 002 s2.4). One bad honeypot answer
   cannot fail a chapter on its own: the worst penalty is −2 against a 75 threshold.
2. **A `uncertain` verifier caps the chapter score below the unlock threshold.** An
   agreement cap that is too strict would need to clamp many scores and would look
   arbitrary on camera; too loose and the verifier changes nothing. Capping at
   ``UNLOCK_THRESHOLD - 1`` (74) meets both: any score the verifier doubted cannot
   unlock the next chapter, and for the recorded "caught" beat the honest reasoning
   score already sits below 74 so the cap never fires visibly. See the note in
   ``apply_verifier`` for the one case where it does bite.
"""
from __future__ import annotations

from typing import Any, Dict, Optional

from .integrity import INTEGRITY_ADJUSTMENT, INTEGRITY_CLEAN, INTEGRITY_ASSISTED
from .state_machine import UNLOCK_THRESHOLD

# Integrity flag -> integrity_score, the 0-100 dimension reported alongside the score.
INTEGRITY_SCORE = {
    INTEGRITY_CLEAN: 100,
    INTEGRITY_ASSISTED: 60,
    "assisted_unverified": 100,
}

# Highest chapter score a verifier may still allow when it did not agree.
UNCERTAIN_VERIFIER_CAP = UNLOCK_THRESHOLD - 1


def chapter_score(
    reasoning_score: int,
    honeypot_points: int,
    integrity_flag: str = INTEGRITY_CLEAN,
) -> Dict[str, Any]:
    """Combine the dimensions exactly as ``ai/core.score_chapter`` does.

    Mirrors the engine formula so a cached run and a live run cannot disagree about
    arithmetic: ``chapter = clamp(reasoning + honeypot + integrity_adjustment, 0, 100)``.
    """
    reasoning = int(reasoning_score)
    honeypot = int(honeypot_points)
    adjustment = INTEGRITY_ADJUSTMENT.get((integrity_flag or INTEGRITY_CLEAN).strip(), 0)
    total = max(0, min(100, reasoning + honeypot + adjustment))
    return {
        "chapter_score": total,
        "reasoning_score": reasoning,
        "integrity_score": INTEGRITY_SCORE.get(
            (integrity_flag or INTEGRITY_CLEAN).strip(), 100
        ),
        "honeypot_score": honeypot,
    }


def apply_verifier(score: Dict[str, Any], verifier: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """Fold the verifier's second opinion into the chapter score.

    ``uncertain`` must be binding, otherwise the verifier loop is decoration and risk R3
    ("LLM grading LLM is subjective") is unmitigated in practice. The cap sits at 74, so
    a doubted score can never unlock.

    The cap deliberately does not rewrite ``reasoning_score``: that field is the engine's
    measurement and stays untouched, so the report can show both the raw reasoning and
    the capped total.
    """
    if not verifier or verifier.get("status") != "uncertain":
        return dict(score)
    capped = dict(score)
    capped["chapter_score"] = min(int(score.get("chapter_score", 0)), UNCERTAIN_VERIFIER_CAP)
    capped["verifier_capped"] = True
    return capped
