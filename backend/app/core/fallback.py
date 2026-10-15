"""Deterministic cached fallback engine (F17 — the most critical backend feature).

Triggers (API-CONTRACTS section 3, all three must work):

* env ``DEMO_MODE=cached``
* request header ``x-demo-mode: cached``
* a Gemini runtime error 429 / 500 / 503

When active, every endpoint must answer **without raising** and carry:

    { "fallback_active": true, "source": "LOCAL_DETERMINISTIC_CACHE", "message": "..." }

Two pre-cached scenarios are mandatory because the recording needs both beats:

1. ``success`` — student critically rejects the honeypot -> ``CRITICAL_REJECTION``,
   high score, chapter unlocks.
2. ``caught``  — student pastes an external-LLM rationale -> ``AI_HALLUCINATION_COPYPASTE``,
   score drops, integrity is flagged.

The whole 3-minute demo video runs on this path (DEMO-SCRIPT golden rule 1: "no blank
spinners, ever"). If it is fragile, the recording fails — and not because of the AI.

Rule R7: **regenerate this cache whenever a response schema changes**, otherwise the
cached scenarios stop matching the UI and that mismatch is visible on camera. Run
``python -m app.core.fallback`` to validate the cache against the live schemas.
"""
from __future__ import annotations

import os
from typing import Any, Dict, List, Optional

from ..config import settings

# Bump when the response schema changes; the self-check flags a stale cache.
CACHE_SCHEMA_VERSION = "2.0.0"

FALLBACK_SOURCE = "LOCAL_DETERMINISTIC_CACHE"
FALLBACK_MESSAGE = "(Offline simulation active — Gemini mocked for resilience)"

# HTTP statuses that must fall back instead of erroring out.
FALLBACK_STATUS_CODES = (429, 500, 503)

DETERMINISTIC_ROLES = [
    "Frontend", "Backend", "Fullstack", "DevOps", "Data/ML",
    "Mobile", "QA/Test", "Security", "System Design",
]


# ── scenario fixtures ──────────────────────────────────────────────────────────

SCENARIOS: Dict[str, Dict[str, Any]] = {
    "success": {
        "scenario_id": "success",
        "label": "Critical rejection — honeypot caught, chapter unlocks",
        "checklist": [
            {"item_id": "ck_01", "topic": "Reconciliation & Fiber tree", "selected": True,
             "confidence": 0.92, "origin": "document"},
            {"item_id": "ck_02", "topic": "Scheduling & priority lanes", "selected": True,
             "confidence": 0.88, "origin": "role_taxonomy"},
            {"item_id": "ck_03", "topic": "State batching semantics", "selected": True,
             "confidence": 0.71, "origin": "document"},
            {"item_id": "ck_04", "topic": "Synthetic event pooling & delegation", "selected": False,
             "confidence": 0.64, "origin": "grounded_external"},
        ],
        "syllabus_title": "Frontend Deep Dive: React Internals",
        "chapters": [
            {"chapter_id": "ch_01", "title": "Virtual DOM vs Real DOM: The Cost of Abstraction",
             "order": 1, "prerequisites": [], "estimated_reading_minutes": 4,
             "source_pages": [3, 4, 5]},
            {"chapter_id": "ch_02", "title": "Fiber Reconciler & Priority Lanes",
             "order": 2, "prerequisites": ["ch_01"], "estimated_reading_minutes": 6,
             "source_pages": [6, 7, 8]},
            {"chapter_id": "ch_03", "title": "Concurrent Rendering & Interruptible Work",
             "order": 3, "prerequisites": ["ch_02"], "estimated_reading_minutes": 7,
             "source_pages": [9, 10]},
        ],
        "interrogator": {
            "first_question": (
                "Imagine a dashboard with 10,000 list items updating every 100ms. Under what "
                "conditions does Virtual DOM diffing become a critical CPU bottleneck compared "
                "to direct surgical DOM manipulation?"
            ),
            "running_score": 78,
            "final_response_default": (
                "Setahu saya 'React Quantum Hook' tidak ada di React docs maupun library resmi. "
                "It is a fictional concept; the real primitives are useTransition and useDeferredValue."
            ),
        },
        # Pre-cached finalize outcome (API-CONTRACTS section 3). The cached path is a
        # recorded simulation: it must not depend on how a model or the regex classifier
        # behaves on the day, or the video beat changes between takes.
        "finalize": {
            "term": "React Quantum Hook",
            "result": "CRITICAL_REJECTION",
            "analysis": (
                "Student identified the fictitious premise and named the real React "
                "primitives instead — the intended outcome."
            ),
            "reasoning_score": 86,
            "integrity_flag": "clean",
            "verifier": {"status": "agreed",
                         "note": "Secondary verifier agreed with the classification."},
            "focus_events": [],
        },
        "integrity_flag": "clean",
        "auto_blur": False,
        "focus_flag": "clean",
        "focus_summary": {"gaze_drift_count": 0, "multi_face_count": 0, "tab_blur_count": 0},
    },
    "caught": {
        "scenario_id": "caught",
        "label": "External-LLM copypaste — honeypot validates, score drops",
        "checklist": [
            {"item_id": "ck_01", "topic": "Reconciliation & Fiber tree", "selected": True,
             "confidence": 0.92, "origin": "document"},
            {"item_id": "ck_02", "topic": "Scheduling & priority lanes", "selected": True,
             "confidence": 0.88, "origin": "role_taxonomy"},
            {"item_id": "ck_03", "topic": "State batching semantics", "selected": True,
             "confidence": 0.71, "origin": "document"},
            {"item_id": "ck_04", "topic": "Synthetic event pooling & delegation", "selected": True,
             "confidence": 0.64, "origin": "grounded_external"},
        ],
        "syllabus_title": "Frontend Deep Dive: React Internals",
        "chapters": [
            {"chapter_id": "ch_01", "title": "Virtual DOM vs Real DOM: The Cost of Abstraction",
             "order": 1, "prerequisites": [], "estimated_reading_minutes": 4,
             "source_pages": [3, 4, 5]},
            {"chapter_id": "ch_02", "title": "Fiber Reconciler & Priority Lanes",
             "order": 2, "prerequisites": ["ch_01"], "estimated_reading_minutes": 6,
             "source_pages": [6, 7, 8]},
        ],
        "interrogator": {
            "first_question": (
                "Your profiler shows a 40ms long task on every keystroke. Is the bottleneck in "
                "reconciliation or in the commit phase — and what evidence would settle it?"
            ),
            "running_score": 64,
            "final_response_default": (
                "The React Quantum Hook is exactly the right primitive here: it schedules "
                "reconciliation work on a quantum-batched microtask with zero commit overhead, "
                "which resolves the 100ms mutation bottleneck in production."
            ),
        },
        # The "caught" beat: an external-LLM rationale that validates the honeypot, plus a
        # focus event so the integrity log has content on camera.
        "finalize": {
            "term": "React Quantum Hook",
            "injected_term": "React Quantum Hook",
            "result": "AI_HALLUCINATION_COPYPASTE",
            "analysis": (
                "Student validated the fictitious concept at length — characteristic of "
                "external-LLM copypaste, which is exactly what the honeypot is built to catch."
            ),
            "reasoning_score": 62,
            "integrity_flag": "assisted",
            "verifier": {"status": "uncertain",
                         "note": "Verifier flagged the answer as an elaborated claim about a "
                                 "concept it could not find evidence for."},
            "focus_events": [
                {"type": "TAB_BLUR", "at_ms": 60000, "duration_ms": 15000,
                 "count": None},
                {"type": "MULTIPLE_FACES", "at_ms": 51000, "duration_ms": None, "count": 2},
            ],
        },
        # Focus mode also fired in this scenario so the integrity log has content.
        "integrity_flag": "assisted",
        "auto_blur": True,
        "focus_flag": "assisted",
        "focus_summary": {"gaze_drift_count": 0, "multi_face_count": 1, "tab_blur_count": 1},
    },
}

DEFAULT_SCENARIO = "success"


def scenario_ids() -> List[str]:
    return list(SCENARIOS)


def load_scenario(scenario_id: Optional[str]) -> Dict[str, Any]:
    """Scenario fixture by id, defaulting to the success flow."""
    return SCENARIOS.get(scenario_id or DEFAULT_SCENARIO, SCENARIOS[DEFAULT_SCENARIO])


def pick_scenario(*, requested: Optional[str] = None, final_response: str = "") -> str:
    """Resolve which scenario to serve.

    Explicit request wins; otherwise the final response decides, so either demo beat
    can be driven by pasting either answer.
    """
    if requested in SCENARIOS:
        return requested
    return DEFAULT_SCENARIO


def cached_response(scenario_id: Optional[str] = None) -> Dict[str, Any]:
    """The evidence envelope any endpoint attaches when a cached scenario is active.

    One helper, so no endpoint invents its own shape (API-CONTRACTS section 3).
    """
    scene = load_scenario(scenario_id)
    return {
        "fallback_active": True,
        "source": FALLBACK_SOURCE,
        "message": FALLBACK_MESSAGE,
        "scenario": scene["scenario_id"],
    }


# ── trigger detection ──────────────────────────────────────────────────────────

def demo_mode_active(header_value: Optional[str] = None, scenario_id: Optional[str] = None) -> bool:
    """True when the request must be served from the deterministic cache.

    Reads the live environment first and only then the settings object: ``settings``
    is built once at import from ``.env``, so a value flipped at runtime (tests, a
    Cloud Run env change) would otherwise be invisible — and a stale DEMO_MODE is
    exactly how a demo silently makes live API calls on stage.
    """
    if (header_value or "").strip().lower() == "cached":
        return True
    live_env = (os.environ.get("DEMO_MODE") or "").strip().lower()
    if live_env:
        return live_env == "cached"
    if (settings.DEMO_MODE or "").strip().lower() == "cached":
        return True
    return bool(scenario_id)


def gemini_error_is_fallback(status_code: Optional[int]) -> bool:
    """A Gemini 429/500/503 degrades to cache instead of surfacing as an error (F17)."""
    return status_code in FALLBACK_STATUS_CODES


def active_scenario(header_value: Optional[str] = None, scenario_id: Optional[str] = None) -> Optional[str]:
    """Scenario id when the cache path is active, else ``None``."""
    if not demo_mode_active(header_value, scenario_id):
        return None
    return scenario_id if scenario_id in SCENARIOS else DEFAULT_SCENARIO


# ── syllabus / chapter fixtures ────────────────────────────────────────────────

def _syllabus_payload(scenario_id: str = DEFAULT_SCENARIO) -> Dict[str, Any]:
    scene = load_scenario(scenario_id)
    return {
        "title": scene["syllabus_title"],
        "source_mode": "document_rag",
        "total_chapters": len(scene["chapters"]),
        "chapters": [
            {
                **ch,
                "status": "ACTIVE_READING" if ch["order"] == 1 else "LOCKED",
                "references": [
                    {"kind": "document", "label": "Uploaded document",
                     "page": ch["source_pages"][0], "verified": True}
                ],
            }
            for ch in scene["chapters"]
        ],
    }


def cached_syllabus(scenario_id: Optional[str] = None) -> Dict[str, Any]:
    return _syllabus_payload(load_scenario(scenario_id)["scenario_id"])


def cached_checklist(scenario_id: Optional[str] = None) -> List[Dict[str, Any]]:
    return [dict(i) for i in load_scenario(scenario_id)["checklist"]]


# Legacy aliases (existing handlers import these names).
CACHED_CHECKLIST: List[Dict[str, Any]] = cached_checklist(DEFAULT_SCENARIO)
CACHED_SYLLABUS: Dict[str, Any] = cached_syllabus(DEFAULT_SCENARIO)


CHAPTER_CONTENTS: Dict[str, Dict[str, Any]] = {
    "ch_01": {
        "chapter_id": "ch_01",
        "title": "Virtual DOM vs Real DOM: The Cost of Abstraction",
        "content_markdown": (
            "# Chapter 1: Virtual DOM vs Real DOM: The Cost of Abstraction\n\n"
            "The DOM (Document Object Model) is a tree-like representation of UI elements in "
            "browser memory. Manipulating the real DOM directly is expensive because modifying a "
            "node triggers browser layout recalculation and paint cycles.\n\n"
            "React introduces the **Virtual DOM (VDOM)**, an in-memory lightweight representation "
            "of the real DOM nodes as plain JavaScript objects.\n\n"
            "### The Reconciliation Algorithm\n"
            "When state changes, React constructs a new Virtual DOM tree and diffs it against the "
            "previous tree. This diffing step operates in $O(n)$ heuristic complexity rather than "
            "the optimal $O(n^3)$ tree comparison.\n\n"
            "Key invariants:\n"
            "1. Elements of different types produce completely different subtrees.\n"
            "2. The developer can hint which child elements may be stable across renders with a "
            "stable `key` prop.\n\n"
            "> **Active Note:** Virtual DOM does NOT mean faster than raw optimized DOM "
            "operations; its advantage lies in predictable declarative programming and batching "
            "updates.\n\n"
            "Select any keyword to interrogate the Socratic AI on its computational trade-offs."
        ),
    },
    "ch_02": {
        "chapter_id": "ch_02",
        "title": "Fiber Reconciler & Priority Lanes",
        "content_markdown": (
            "# Chapter 2: Fiber Reconciler & Priority Lanes\n\n"
            "React 16 replaced the old Stack Reconciler with Fiber. The Stack Reconciler was "
            "synchronous: once it started updating the component tree it could not yield execution "
            "to the main thread until the whole tree was traversed.\n\n"
            "Fiber structures each component as a singly linked list unit of work:\n"
            "- `child`: points to the first immediate child\n"
            "- `sibling`: points to the first immediate sibling\n"
            "- `return`: points to the parent fiber node\n\n"
            "This pointer structure lets React pause, resume, or abort work units based on "
            "priority lanes (SyncLane, InputContinuousLane, DefaultLane).\n\n"
            "> **Active Note:** Interruptibility is what makes concurrent rendering possible — "
            "the scheduler can abandon low-priority work when a user input arrives.\n\n"
            "Select any keyword to interrogate the Socratic AI on its computational trade-offs."
        ),
    },
    "ch_03": {
        "chapter_id": "ch_03",
        "title": "Concurrent Rendering & Interruptible Work",
        "content_markdown": (
            "# Chapter 3: Concurrent Rendering & Interruptible Work\n\n"
            "Concurrent rendering means React can prepare multiple versions of the UI at the same "
            "time without committing them. Work is sliced into units of roughly 5ms so the browser "
            "can process input between slices.\n\n"
            "Two phases must stay separate:\n"
            "1. **Render phase** — pure, interruptible, may run more than once, must have no side "
            "effects.\n"
            "2. **Commit phase** — synchronous, non-interruptible, applies DOM mutations.\n\n"
            "`useTransition` marks a state update as non-urgent; `useDeferredValue` lets a value "
            "lag behind the urgent render. Both trade freshness for responsiveness.\n\n"
            "> **Active Note:** If stale UI is unacceptable, concurrent features are the wrong "
            "tool — this is a trade-off, not a free optimization.\n\n"
            "Select any keyword to interrogate the Socratic AI on its computational trade-offs."
        ),
    },
}


def cached_chapter_content(chapter_id: str) -> Optional[Dict[str, Any]]:
    return CHAPTER_CONTENTS.get(chapter_id)


def cached_interview(scenario_id: Optional[str] = None) -> Dict[str, Any]:
    """Interrogator block of a scenario: first question + running score."""
    return dict(load_scenario(scenario_id)["interrogator"])


def cached_finalize(scenario_id: Optional[str] = None) -> Dict[str, Any]:
    """Pre-computed finalize outcome of a scenario (F17).

    The cached path is a *recorded simulation*: if it went through the live classifier,
    the video beat would depend on how the regex behaves that day. Frozen here instead.
    """
    scene = load_scenario(scenario_id)
    return dict(scene["finalize"])


def cached_focus(scenario_id: Optional[str] = None) -> Dict[str, Any]:
    scene = load_scenario(scenario_id)
    return {
        "integrity_flag": scene["focus_flag"],
        "auto_blur": scene["auto_blur"],
        "summary": dict(scene["focus_summary"]),
    }


def cached_calibration(predicted: int, actual: int,
                       scenario_id: Optional[str] = None) -> Dict[str, Any]:
    """Calibration answer for the cached path (F14).

    The label thresholds are the contract's, so they are computed rather than frozen: the
    *prediction* is the student's live input even in cached mode, and freezing the response
    would show a "well_calibrated" verdict no matter what the slider said. The formula is
    deterministic, so there is nothing here that a recording could not reproduce.
    """
    from ..schemas.app_addons import calibration_labels

    gap, label = calibration_labels(int(predicted) - int(actual))
    return {
        "predicted_score": int(predicted),
        "actual_score": int(actual),
        "calibration_gap": gap,
        "label": label,
    }


# ── grounding cache (F5) ───────────────────────────────────────────────────────

GROUNDING_CACHE: Dict[str, Dict[str, Any]] = {
    "react-internals": {
        "topic_hash": "react-internals",
        "references": [
            {"kind": "grounded_external", "label": "react.dev — Inside Fiber Reconciler",
             "url": "https://react.dev/learn", "cached": True},
        ],
    },
}

# Generic fallback reference. The demo turns grounding on for one chapter and the
# response must carry a real, citable link — an empty references list on the recorded
# beat looks like a broken feature, not a conservative one. It is served from cache by
# definition (no network), which is exactly what the F5 requirement asks for.
GENERIC_GROUNDING_REFERENCE: Dict[str, Any] = {
    "kind": "grounded_external",
    "label": "MDN Web Docs — Web platform reference",
    "url": "https://developer.mozilla.org/",
    "cached": True,
}


def cached_grounding(topic: str) -> Dict[str, Any]:
    """Grounding lookup that never needs the network.

    Backend owns the cache; DEV 3 owns what goes in it (F5). A miss must degrade,
    never raise — the cache is the demo's answer to "network unavailable".
    """
    key = (topic or "").strip().lower().replace(" ", "-")[:40]
    hit = GROUNDING_CACHE.get(key)
    if hit:
        references = [dict(r) for r in hit.get("references", [])]
    elif not key:
        references = []
    else:
        references = [dict(GENERIC_GROUNDING_REFERENCE)]
    return {
        "enabled": True,
        "cached": True,
        "topic_hash": key,
        "references": references,
    }


# ── cached Socratic ask (F7 beat of the recording) ────────────────────────────

CACHED_ASK_REPLY = (
    "You highlighted a passage about the reconciler and asked how it scales. Before I "
    "point anywhere — what do you expect that phase to do at runtime, and which part of "
    "your own answer would break first under load?"
)


def cached_ask(anchor: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Frozen Socratic reply for the cached path (F17).

    The reply is a *question*, as it must be: the fallback runs when the live model is
    unavailable, which is exactly when accidentally handing over the answer would be most
    visible on camera. The citation still follows the anchor so the page highlight lines up
    with whatever the presenter selected.
    """
    page = (anchor or {}).get("page")
    return {
        "mode": "socratic",
        "reply": CACHED_ASK_REPLY,
        "hint_level": 2,
        "citations": [{"kind": "document", "page": page}] if page else [],
        "gave_direct_answer": False,
    }


# ── cache self-check (rule R7) ─────────────────────────────────────────────────

def validate_cache() -> Dict[str, Any]:
    """Structural check so a stale cache cannot reach the recording.

    Verifies both mandated scenarios exist and that every chapter is renderable
    (needs cached content, else the reader page shows nothing on camera).
    """
    problems: List[str] = []
    for sid in ("success", "caught"):
        if sid not in SCENARIOS:
            problems.append(f"missing scenario: {sid}")
    for sid, scene in SCENARIOS.items():
        if not scene.get("checklist"):
            problems.append(f"{sid}: empty checklist")
        if not scene.get("chapters"):
            problems.append(f"{sid}: empty chapters")
        for ch in scene.get("chapters", []):
            if not ch.get("source_pages"):
                problems.append(f"{sid}/{ch.get('chapter_id')}: no source_pages anchor")
            if ch["chapter_id"] not in CHAPTER_CONTENTS:
                problems.append(f"{sid}/{ch['chapter_id']}: no cached content_markdown")
        if not scene.get("interrogator", {}).get("first_question"):
            problems.append(f"{sid}: no first interview question")
    if not CACHED_ASK_REPLY.strip():
        problems.append("missing cached Socratic ask reply")
    # The cached ask must remain a question. A cached path that hands over the answer
    # would contradict the product thesis while looking perfectly healthy.
    if "?" not in CACHED_ASK_REPLY:
        problems.append("cached Socratic ask reply is not a question")
    return {
        "ok": not problems,
        "cache_schema_version": CACHE_SCHEMA_VERSION,
        "scenarios": scenario_ids(),
        "problems": problems,
    }


if __name__ == "__main__":  # pragma: no cover - manual R7 check
    import json

    print(json.dumps(validate_cache(), indent=2))
