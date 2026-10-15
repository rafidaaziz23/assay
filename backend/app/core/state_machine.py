"""Chapter lifecycle state machine (API-CONTRACTS section 1).

    LOCKED -> ACTIVE_READING -> INTERVIEW -> SCORED -> UNLOCKED | NEEDS_REVIEW

Two invariants that must not be broken:

1. The backend owns this state (DEV 2 breakdown F3/F6/F9). The frontend only *reads*
   ``next_locked``; if the backend forgets to maintain it, the gate is empty.
2. Honeypot does NOT change state — it only fills ``honeypot_score`` inside the score
   (API-CONTRACTS section 1). Honeypot is a score dimension, never a gate (ADR 002).

``NEEDS_REVIEW`` is a retry, not a dead end: a chapter can go back to INTERVIEW.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from ..repositories import InMemoryStore, get_store

LOCKED = "LOCKED"
ACTIVE_READING = "ACTIVE_READING"
INTERVIEW = "INTERVIEW"
SCORED = "SCORED"
UNLOCKED = "UNLOCKED"
NEEDS_REVIEW = "NEEDS_REVIEW"

CHAPTER_STATES = (LOCKED, ACTIVE_READING, INTERVIEW, SCORED, UNLOCKED, NEEDS_REVIEW)

# Pass threshold for unlocking the next chapter (PRD section 3 Step 6).
UNLOCK_THRESHOLD = 75

ALLOWED_TRANSITIONS: Dict[str, tuple] = {
    LOCKED: (ACTIVE_READING,),
    ACTIVE_READING: (INTERVIEW,),
    INTERVIEW: (SCORED,),
    SCORED: (UNLOCKED, NEEDS_REVIEW),
    # Retry path: a failed chapter re-enters the interview, or is re-scored after an
    # accepted appeal (F15).
    NEEDS_REVIEW: (INTERVIEW, SCORED, UNLOCKED),
    UNLOCKED: (),
}


class InvalidTransition(ValueError):
    """Raised when code tries to move a chapter along an edge that does not exist."""


def can_transition(current: str, target: str) -> bool:
    return target in ALLOWED_TRANSITIONS.get(current, ())


def transition(chapter_id: str, target: str, store: Optional[InMemoryStore] = None) -> Dict[str, Any]:
    """Move a chapter to ``target``, refusing illegal edges."""
    store = store or get_store()
    chapter = store.get_chapter(chapter_id)
    if chapter is None:
        raise KeyError(f"unknown chapter: {chapter_id}")
    current = chapter.get("status", LOCKED)
    if current == target:
        return chapter
    if not can_transition(current, target):
        raise InvalidTransition(f"{chapter_id}: {current} -> {target} is not allowed")
    store.set_chapter_status(chapter_id, target)
    if target in (UNLOCKED, NEEDS_REVIEW, LOCKED, ACTIVE_READING):
        store.refresh_next_locked(chapter_id)
    return chapter


def start_interview_state(chapter_id: str, store: Optional[InMemoryStore] = None) -> Dict[str, Any]:
    """ACTIVE_READING -> INTERVIEW. A retry from NEEDS_REVIEW is allowed too."""
    store = store or get_store()
    chapter = store.get_chapter(chapter_id)
    if chapter is None:
        raise KeyError(f"unknown chapter: {chapter_id}")
    current = chapter.get("status", LOCKED)
    if current == INTERVIEW:
        return chapter
    if current in (LOCKED,):
        raise InvalidTransition(f"{chapter_id}: cannot start an interview while {current}")
    if current == SCORED:
        # Re-scoring after an accepted appeal must go through NEEDS_REVIEW first.
        raise InvalidTransition(f"{chapter_id}: chapter already scored")
    store.set_chapter_status(chapter_id, INTERVIEW)
    return chapter


def apply_score(
    chapter_id: str,
    score: Dict[str, Any],
    store: Optional[InMemoryStore] = None,
) -> Dict[str, Any]:
    """INTERVIEW -> SCORED, then SCORED -> UNLOCKED / NEEDS_REVIEW by threshold.

    Returns ``{passed, status, next_unlocked_chapter_id}``. The next chapter moves to
    ACTIVE_READING only when this one passes; the last chapter has no successor.

    If the chapter was already UNLOCKED, the result is re-applied without re-opening the
    next chapter. That is the appeal path (F15): a re-scored chapter must not push every
    successor back through the gate, and a re-score that fails must be able to take the
    unlock away again (the student's transcript has to stay truthful).
    """
    store = store or get_store()
    chapter = store.get_chapter(chapter_id)
    if chapter is None:
        raise KeyError(f"unknown chapter: {chapter_id}")

    chapter_score = int(score.get("chapter_score", 0))
    passed = chapter_score >= UNLOCK_THRESHOLD

    # A retry from NEEDS_REVIEW re-scores directly (NEEDS_REVIEW -> SCORED is legal), and
    # an accepted appeal re-scores from UNLOCKED.
    if chapter.get("status") not in (INTERVIEW, SCORED, NEEDS_REVIEW, UNLOCKED):
        raise InvalidTransition(f"{chapter_id}: cannot score while {chapter.get('status')}")

    was_unlocked = chapter.get("status") == UNLOCKED
    store.set_chapter_status(chapter_id, SCORED)
    chapter["score"] = dict(score)

    target = UNLOCKED if passed else NEEDS_REVIEW
    store.set_chapter_status(chapter_id, target)

    next_id = None
    if passed:
        nxt = store.next_chapter(chapter_id)
        if nxt is not None:
            next_id = nxt["chapter_id"]
            # Never rewind a successor the student has already progressed past: only a
            # fresh LOCKED successor is opened up.
            if nxt.get("status") == LOCKED:
                store.set_chapter_status(next_id, ACTIVE_READING)
        chapter["next_locked"] = False
    elif was_unlocked:
        # An appeal knocked the chapter back below the threshold: the gate has to close
        # again, otherwise the unlock would be permanent after the first pass.
        nxt = store.next_chapter(chapter_id)
        if nxt is not None:
            next_id = nxt["chapter_id"]

    store.refresh_next_locked(chapter_id)
    if next_id:
        store.refresh_next_locked(next_id)

    chapter.setdefault("pass_history", []).append(
        {"chapter_score": chapter_score, "passed": passed, "status": target}
    )
    return {"passed": passed, "status": target, "next_unlocked_chapter_id": next_id if passed else None}


def apply_appeal_outcome(
    chapter_id: str,
    outcome: str,
    score: Optional[Dict[str, Any]] = None,
    store: Optional[InMemoryStore] = None,
) -> Dict[str, Any]:
    """Apply an appeal decision to a chapter (F15).

    Appeals arrive asynchronously and the demo never waits for the verdict, so the mapping
    from the engine's vocabulary to the state machine lives here in one place:

    * ``upheld``        -> no state change. The original score stands.
    * ``score_revised`` -> re-apply the new score through ``apply_score``, which is what
      decides UNLOCKED vs NEEDS_REVIEW. Never write the status directly.
    * ``re_interview``  -> the chapter returns to NEEDS_REVIEW and can be retried.

    Anything else is a no-op: an unrecognised verdict must not silently unlock a chapter.
    """
    store = store or get_store()
    chapter = store.get_chapter(chapter_id)
    if chapter is None:
        raise KeyError(f"unknown chapter: {chapter_id}")

    if outcome == "upheld":
        return {"applied": False, "status": chapter.get("status"), "reason": "upheld"}

    if outcome == "score_revised":
        revised = dict(score or chapter.get("score") or {})
        if "chapter_score" not in revised:
            return {"applied": False, "status": chapter.get("status"),
                    "reason": "no revised score supplied"}
        result = apply_score(chapter_id, revised, store=store)
        return {"applied": True, "status": result["status"],
                "reason": "score_revised", **result}

    if outcome == "re_interview":
        store.set_chapter_status(chapter_id, NEEDS_REVIEW)
        store.refresh_next_locked(chapter_id)
        return {"applied": True, "status": NEEDS_REVIEW, "reason": "re_interview"}

    return {"applied": False, "status": chapter.get("status"), "reason": "unknown outcome"}


def record_calibration(
    chapter_id: str,
    payload: Dict[str, Any],
    store: Optional[InMemoryStore] = None,
) -> Dict[str, Any]:
    """Store the calibration result on the chapter (never a gate — PRD section 3)."""
    store = store or get_store()
    chapter = store.get_chapter(chapter_id)
    if chapter is None:
        raise KeyError(f"unknown chapter: {chapter_id}")
    chapter["calibration"] = dict(payload)
    return chapter


def initialize_from_syllabus(
    session_id: str,
    chapters: List[Dict[str, Any]],
    store: Optional[InMemoryStore] = None,
) -> List[Dict[str, Any]]:
    """Persist syllabus chapters and seed the state machine (F3).

    ``order == 1`` starts ACTIVE_READING, everything else LOCKED. State lives here,
    not in the AI engine.
    """
    store = store or get_store()
    persisted: List[Dict[str, Any]] = []
    for raw in sorted(chapters, key=lambda c: c.get("order", 0)):
        order = int(raw.get("order", 1))
        record = {
            **raw,
            "session_id": session_id,
            "order": order,
            "status": ACTIVE_READING if order == 1 else LOCKED,
        }
        persisted.append(store.put_chapter(record))
    for record in persisted:
        store.refresh_next_locked(record["chapter_id"])
    return persisted


# ── legacy facade ──────────────────────────────────────────────────────────────
# Handlers that predate the repository layer mutate ``store`` directly. This keeps
# them (and their tests) working while endpoints migrate to the helpers above.

class _StoreFacade:
    """Attribute passthrough to the process-wide store."""

    def __getattr__(self, item: str) -> Any:
        return getattr(get_store(), item)

    def __setattr__(self, key: str, value: Any) -> None:
        setattr(get_store(), key, value)


store = _StoreFacade()
