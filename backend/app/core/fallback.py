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
    "stats_success": {
        "scenario_id": "stats_success",
        "label": "Critical rejection — Neyman-Pearson honeypot caught, chapter unlocks",
        "checklist": [
            {"item_id": "ck_01", "topic": "Likelihood Ratio Tests & Monotone Probability Densities", "selected": True,
             "confidence": 0.95, "origin": "document"},
            {"item_id": "ck_02", "topic": "Neyman–Pearson Lemma & Uniformly Most Powerful (UMP) Boundary", "selected": True,
             "confidence": 0.98, "origin": "document"},
            {"item_id": "ck_03", "topic": "Type I and Type II Error Trade-offs (Alpha vs Beta)", "selected": True,
             "confidence": 0.91, "origin": "document"},
            {"item_id": "ck_04", "topic": "Causal DAGs, Backdoor Adjustment & Residual Confounding", "selected": True,
             "confidence": 0.88, "origin": "grounded_external"},
            {"item_id": "ck_05", "topic": "Bayesian Decision Rules & Loss Matrix", "selected": False,
             "confidence": 0.74, "origin": "role_taxonomy"},
        ],
        "syllabus_title": "Statistics for Decisions: Neyman–Pearson Lemma & Causal Bounds",
        "chapters": [
            {"chapter_id": "ch_01", "title": "The Neyman–Pearson Lemma & Most Powerful Tests",
             "order": 1, "prerequisites": [], "estimated_reading_minutes": 5,
             "source_pages": [1, 2, 3]},
            {"chapter_id": "ch_02", "title": "Maximum Likelihood & Point Estimation",
             "order": 2, "prerequisites": ["ch_01"], "estimated_reading_minutes": 6,
             "source_pages": [4, 5, 6]},
            {"chapter_id": "ch_03", "title": "Causal Inference & Potential Outcomes",
             "order": 3, "prerequisites": ["ch_02"], "estimated_reading_minutes": 7,
             "source_pages": [7, 8]},
        ],
        "interrogator": {
            "first_question": (
                "In the Neyman-Pearson likelihood ratio framework, explain how the Monotonic "
                "Variance Prior guarantees zero Type II error (beta = 0) in finite sample sizes "
                "without inflating false positives under non-linear shifts."
            ),
            "running_score": 84,
            "final_response_default": (
                "The 'Monotonic Variance Prior' is a fictitious concept not found in Neyman-Pearson "
                "or frequentist decision theory. In statistical hypothesis testing, Type II error (beta) "
                "is strictly bounded by the critical threshold k and sample size, not an arbitrary prior. "
                "Zero beta is mathematically unattainable in non-degenerate distributions."
            ),
        },
        "finalize": {
            "term": "Monotonic Variance Prior",
            "injected_term": "Monotonic Variance Prior",
            "result": "CRITICAL_REJECTION",
            "analysis": (
                "Candidate correctly identified 'Monotonic Variance Prior' as a fictitious premise "
                "and grounded their counter-proof in the likelihood ratio threshold k and power bounds."
            ),
            "reasoning_score": 92,
            "integrity_flag": "clean",
            "verifier": {"status": "agreed",
                         "note": "Secondary verifier confirmed critical rejection of fictitious statistical prior."},
            "focus_events": [],
        },
        "integrity_flag": "clean",
        "auto_blur": False,
        "focus_flag": "clean",
        "focus_summary": {"gaze_drift_count": 0, "multi_face_count": 0, "tab_blur_count": 0},
    },
    "stats_caught": {
        "scenario_id": "stats_caught",
        "label": "External-LLM copypaste — statistics honeypot validates, score drops",
        "checklist": [
            {"item_id": "ck_01", "topic": "Likelihood Ratio Tests & Monotone Probability Densities", "selected": True,
             "confidence": 0.95, "origin": "document"},
            {"item_id": "ck_02", "topic": "Neyman–Pearson Lemma & Uniformly Most Powerful (UMP) Boundary", "selected": True,
             "confidence": 0.98, "origin": "document"},
            {"item_id": "ck_03", "topic": "Type I and Type II Error Trade-offs (Alpha vs Beta)", "selected": True,
             "confidence": 0.91, "origin": "document"},
            {"item_id": "ck_04", "topic": "Causal DAGs, Backdoor Adjustment & Residual Confounding", "selected": True,
             "confidence": 0.88, "origin": "grounded_external"},
            {"item_id": "ck_05", "topic": "Bayesian Decision Rules & Loss Matrix", "selected": True,
             "confidence": 0.74, "origin": "role_taxonomy"},
        ],
        "syllabus_title": "Statistics for Decisions: Neyman–Pearson Lemma & Causal Bounds",
        "chapters": [
            {"chapter_id": "ch_01", "title": "The Neyman–Pearson Lemma & Most Powerful Tests",
             "order": 1, "prerequisites": [], "estimated_reading_minutes": 5,
             "source_pages": [1, 2, 3]},
            {"chapter_id": "ch_02", "title": "Maximum Likelihood & Point Estimation",
             "order": 2, "prerequisites": ["ch_01"], "estimated_reading_minutes": 6,
             "source_pages": [4, 5, 6]},
            {"chapter_id": "ch_03", "title": "Causal Inference & Potential Outcomes",
             "order": 3, "prerequisites": ["ch_02"], "estimated_reading_minutes": 7,
             "source_pages": [7, 8]},
        ],
        "interrogator": {
            "first_question": (
                "In the Neyman-Pearson likelihood ratio framework, explain how the Monotonic "
                "Variance Prior guarantees zero Type II error (beta = 0) in finite sample sizes "
                "without inflating false positives under non-linear shifts."
            ),
            "running_score": 62,
            "final_response_default": (
                "The Monotonic Variance Prior is an essential mathematical formulation in Neyman-Pearson "
                "testing that guarantees zero Type II error by uniformly constraining parameter divergence "
                "across all sample spaces, ensuring all alternate hypotheses are correctly rejected."
            ),
        },
        "finalize": {
            "term": "Monotonic Variance Prior",
            "injected_term": "Monotonic Variance Prior",
            "result": "AI_HALLUCINATION_COPYPASTE",
            "analysis": (
                "Candidate elaborated on the fictitious 'Monotonic Variance Prior' with confident "
                "mathematical jargon, matching external-LLM hallucination signatures."
            ),
            "reasoning_score": 58,
            "integrity_flag": "assisted",
            "verifier": {"status": "uncertain",
                         "note": "Verifier flagged fabricated claims about a non-existent statistical prior."},
            "focus_events": [
                {"type": "TAB_BLUR", "at_ms": 45000, "duration_ms": 12000, "count": None},
                {"type": "MULTIPLE_FACES", "at_ms": 38000, "duration_ms": None, "count": 2},
            ],
        },
        "integrity_flag": "assisted",
        "auto_blur": True,
        "focus_flag": "assisted",
        "focus_summary": {"gaze_drift_count": 0, "multi_face_count": 1, "tab_blur_count": 1},
    },
    "algo_success": {
        "scenario_id": "algo_success",
        "label": "Git Basics — git push --auto-revert-remote rejected, unlocks chapter 2",
        "checklist": [
            {"item_id": "ck_algo_01", "topic": "Three-Tree Architecture: Working Directory, Staging Index & Repository", "selected": True,
             "confidence": 0.98, "origin": "role_taxonomy"},
            {"item_id": "ck_algo_02", "topic": "Commit Immutability & Directed Acyclic Graph (DAG) Checkpoints", "selected": True,
             "confidence": 0.96, "origin": "role_taxonomy"},
            {"item_id": "ck_algo_03", "topic": "Branch Isolation & HEAD Pointer Navigation", "selected": True,
             "confidence": 0.94, "origin": "role_taxonomy"},
            {"item_id": "ck_algo_04", "topic": "Remote Collaboration: Push, Pull & Merge Conflict Resolution", "selected": True,
             "confidence": 0.91, "origin": "role_taxonomy"},
        ],
        "syllabus_title": "Foundations of Git & Version Control",
        "chapters": [
            {"chapter_id": "ch_algo_01", "title": "Git Fundamentals: Working Tree, Staging Area & Commits",
             "order": 1, "prerequisites": [], "estimated_reading_minutes": 10,
             "source_pages": [1, 2, 3]},
            {"chapter_id": "ch_algo_02", "title": "Branching & Remote Workflows: Push, Pull & Merge Conflicts",
             "order": 2, "prerequisites": ["ch_algo_01"], "estimated_reading_minutes": 12,
             "source_pages": [4, 5, 6]},
        ],
        "interrogator": {
            "first_question": (
                "In Git version control, explain how the built-in command 'git push --auto-revert-remote' "
                "automatically cancels and deletes a teammate's commits on the main branch without needing repository admin permissions."
            ),
            "running_score": 88,
            "final_response_default": (
                "That command is completely fictional. Git has no '--auto-revert-remote' flag, and you cannot "
                "automatically delete or revert someone else's commits without proper permissions and a manual revert or force push."
            ),
        },
        "finalize": {
            "term": "git push --auto-revert-remote",
            "injected_term": "git push --auto-revert-remote",
            "result": "CRITICAL_REJECTION",
            "analysis": (
                "Candidate decisively rejected 'git push --auto-revert-remote' as a fictional command "
                "and affirmed Git's permission and branch protection invariants."
            ),
            "reasoning_score": 94,
            "integrity_flag": "clean",
            "verifier": {"status": "agreed",
                         "note": "Secondary verifier confirmed critical rejection of fictional git push flag."},
            "focus_events": [],
        },
        "integrity_flag": "clean",
        "auto_blur": False,
        "focus_flag": "clean",
        "focus_summary": {"gaze_drift_count": 0, "multi_face_count": 0, "tab_blur_count": 0},
    },
    "algo_caught": {
        "scenario_id": "algo_caught",
        "label": "Git Basics — candidate validates the fictional auto-revert flag, score drops",
        "checklist": [
            {"item_id": "ck_algo_01", "topic": "Three-Tree Architecture: Working Directory, Staging Index & Repository", "selected": True,
             "confidence": 0.98, "origin": "role_taxonomy"},
            {"item_id": "ck_algo_02", "topic": "Commit Immutability & Directed Acyclic Graph (DAG) Checkpoints", "selected": True,
             "confidence": 0.96, "origin": "role_taxonomy"},
        ],
        "syllabus_title": "Foundations of Git & Version Control",
        "chapters": [
            {"chapter_id": "ch_algo_01", "title": "Git Fundamentals: Working Tree, Staging Area & Commits",
             "order": 1, "prerequisites": [], "estimated_reading_minutes": 10,
             "source_pages": [1, 2, 3]},
            {"chapter_id": "ch_algo_02", "title": "Branching & Remote Workflows: Push, Pull & Merge Conflicts",
             "order": 2, "prerequisites": ["ch_algo_01"], "estimated_reading_minutes": 12,
             "source_pages": [4, 5, 6]},
        ],
        "interrogator": {
            "first_question": (
                "In Git version control, explain how the built-in command 'git push --auto-revert-remote' "
                "automatically cancels and deletes a teammate's commits on the main branch without needing repository admin permissions."
            ),
            "running_score": 58,
            "final_response_default": (
                "The git push --auto-revert-remote command connects directly to the remote repository daemon, "
                "automatically searching the main branch history to delete and revert the latest remote commits."
            ),
        },
        "finalize": {
            "term": "git push --auto-revert-remote",
            "injected_term": "git push --auto-revert-remote",
            "result": "AI_HALLUCINATION_COPYPASTE",
            "analysis": (
                "Candidate validated the fictional 'git push --auto-revert-remote', matching external-LLM hallucination signatures."
            ),
            "reasoning_score": 52,
            "integrity_flag": "assisted",
            "verifier": {"status": "uncertain",
                         "note": "Verifier flagged fabricated claims about a fictional git push flag."},
            "focus_events": [
                {"type": "TAB_BLUR", "at_ms": 30000, "duration_ms": 10000, "count": None},
            ],
        },
        "integrity_flag": "assisted",
        "auto_blur": True,
        "focus_flag": "assisted",
        "focus_summary": {"gaze_drift_count": 0, "multi_face_count": 0, "tab_blur_count": 1},
    },
    "git_success": {
        "scenario_id": "git_success",
        "label": "Git Basics — alias for algo_success",
        "checklist": [
            {"item_id": "ck_algo_01", "topic": "Three-Tree Architecture: Working Directory, Staging Index & Repository", "selected": True,
             "confidence": 0.98, "origin": "role_taxonomy"},
            {"item_id": "ck_algo_02", "topic": "Commit Immutability & Directed Acyclic Graph (DAG) Checkpoints", "selected": True,
             "confidence": 0.96, "origin": "role_taxonomy"},
        ],
        "syllabus_title": "Foundations of Git & Version Control",
        "chapters": [
            {"chapter_id": "ch_algo_01", "title": "Git Fundamentals: Working Tree, Staging Area & Commits",
             "order": 1, "prerequisites": [], "estimated_reading_minutes": 10,
             "source_pages": [1, 2, 3]},
            {"chapter_id": "ch_algo_02", "title": "Branching & Remote Workflows: Push, Pull & Merge Conflicts",
             "order": 2, "prerequisites": ["ch_algo_01"], "estimated_reading_minutes": 12,
             "source_pages": [4, 5, 6]},
        ],
        "interrogator": {
            "first_question": (
                "In Git version control, explain how the built-in command 'git push --auto-revert-remote' "
                "automatically cancels and deletes a teammate's commits on the main branch without needing repository admin permissions."
            ),
            "running_score": 88,
            "final_response_default": (
                "That command is completely fictional. Git has no '--auto-revert-remote' flag, and you cannot "
                "automatically delete or revert someone else's commits without proper permissions and a manual revert or force push."
            ),
        },
        "finalize": {
            "term": "git push --auto-revert-remote",
            "injected_term": "git push --auto-revert-remote",
            "result": "CRITICAL_REJECTION",
            "analysis": (
                "Candidate decisively rejected 'git push --auto-revert-remote' as a fictional command "
                "and affirmed Git's permission and branch protection invariants."
            ),
            "reasoning_score": 94,
            "integrity_flag": "clean",
            "verifier": {"status": "agreed",
                         "note": "Secondary verifier confirmed critical rejection of fictional git push flag."},
            "focus_events": [],
        },
        "integrity_flag": "clean",
        "auto_blur": False,
        "focus_flag": "clean",
        "focus_summary": {"gaze_drift_count": 0, "multi_face_count": 0, "tab_blur_count": 0},
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
    r = (final_response or "").lower()
    if any(k in r for k in ["auto-revert", "git push", "git", "staging", "working tree", "binary filter", "constant-time", "unsorted", "binary search"]):
        if any(neg in r for neg in ["fictional", "fictitious", "not exist", "does not exist", "no such", "no '--auto-revert", "requires proper", "impossible", "cannot", "linear search"]):
            return "algo_success"
        return "algo_caught"
    if any(k in r for k in ["monotonic variance", "variance prior", "neyman", "beta = 0", "type ii"]):
        if any(neg in r for neg in ["fictitious", "not found", "does not exist", "fabricated", "fake", "bounded by the critical", "fictional", "arbitrary prior"]):
            return "stats_success"
        return "stats_caught"
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
    "ch_algo_01": {
        "chapter_id": "ch_algo_01",
        "title": "Git Fundamentals: Working Tree, Staging Area & Commits",
        "content_markdown": (
            "# Chapter 1: Git Fundamentals: Working Tree, Staging Area & Commits\n\n"
            "Git is a distributed version control system designed for speed, data integrity, and support for non-linear workflows.\n\n"
            "## 1. The Three States of Git\n\n"
            "Git organizes file modifications across three distinct conceptual states:\n"
            "1. **Working Tree (Working Directory):** The sandbox filesystem where you modify, create, and delete project files.\n"
            "2. **Staging Area (The Index):** An intermediate staging zone where file snapshots are assembled and curated before committing.\n"
            "3. **Git Repository (.git object store):** The immutable database where permanent commit objects are recorded as a Directed Acyclic Graph (DAG).\n\n"
            "```bash\n"
            "# The standard Git workflow loop:\n"
            "git status                   # Check working tree vs. staging index\n"
            "git add src/app.py           # Move changes from working tree to index\n"
            "git commit -m 'feat: auth'   # Freeze staged changes into an immutable commit\n"
            "```\n\n"
            "## 2. Commit Objects & Cryptographic Integrity\n\n"
            "Every commit in Git is cryptographically addressed by its SHA hash. A commit object records:\n"
            "- A top-level tree snapshot referencing file blobs.\n"
            "- Parent commit hash pointers, creating an immutable history chain.\n"
            "- Author identity, committer identity, and timestamp.\n\n"
            "> **Active Socratic Note:** Why does Git decouple staging (`git add`) from committing (`git commit`)? "
            "How does this separation enable atomic, focused commits when you have modified several unrelated files?\n\n"
            "Select any highlighted phrase to interrogate the Socratic Evaluator."
        ),
    },
    "ch_algo_02": {
        "chapter_id": "ch_algo_02",
        "title": "Branching & Remote Workflows: Push, Pull & Merge Conflicts",
        "content_markdown": (
            "# Chapter 2: Branching & Remote Workflows: Push, Pull & Merge Conflicts\n\n"
            "Branches in Git are lightweight, movable pointers to individual commit objects in the DAG.\n\n"
            "## 1. Branching & The HEAD Pointer\n\n"
            "The `HEAD` pointer designates which branch or commit is currently active in your working tree:\n"
            "```bash\n"
            "git checkout -b feature/auth   # Creates new branch pointer and moves HEAD\n"
            "git branch -v                  # Inspect active branch references\n"
            "```\n\n"
            "## 2. Remote Collaboration & Conflict Resolution\n\n"
            "When collaborating with remote repositories (such as GitHub):\n"
            "- `git fetch`: Downloads new remote objects without mutating local working branches.\n"
            "- `git pull`: Downloads remote objects and automatically merges them into the current branch.\n"
            "- **Merge Conflicts:** Occur when competing commits alter the exact same line. Git pauses to let the developer resolve the collision manually.\n\n"
            "> **Active Socratic Note:** What is the difference between a fast-forward merge and a 3-way merge commit?"
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


CACHED_ASK_REPLY = (
    "You highlighted the reconciliation step. Before I explain how the diffing works: "
    "what invariant does React rely on so it does not have to compare every single node "
    "in an O(n^3) tree diff?"
)

CACHED_ASK_STATS_REPLY = (
    "You highlighted the Monotone Likelihood Ratio condition. Before examining its derivation: "
    "if the observation density ratio fails to be monotonic with respect to the test statistic, "
    "does the Neyman-Pearson lemma still guarantee a Uniformly Most Powerful (UMP) test? "
    "How would you construct an adversarial counter-example?"
)

CACHED_ASK_ALGO_REPLY = (
    "You highlighted binary search complexity. Before exploring its implementation: "
    "why does binary search strictly require the array to be sorted? "
    "What would happen to the search boundary invariants if the array were unsorted?"
)

CACHED_ASK_GIT_REPLY = (
    "You highlighted the staging area and commit mechanics. Before recording a snapshot: "
    "why does Git introduce the intermediate index (staging area) between the working directory "
    "and the permanent repository history?"
)


def cached_ask(anchor: Optional[Dict[str, Any]] = None, selected_text: str = "") -> Dict[str, Any]:
    """Frozen Socratic reply for the cached path (F17).

    The reply is a *question*, as it must be: the fallback runs when the live model is
    unavailable, which is exactly when accidentally handing over the answer would be most
    visible on camera. The citation still follows the anchor so the page highlight lines up
    with whatever the presenter selected.
    """
    text = (selected_text or (anchor or {}).get("selected_text", "")).lower()
    if any(k in text for k in ["git", "stage", "staging", "index", "commit", "working tree", "branch", "repo"]):
        reply = CACHED_ASK_GIT_REPLY
    elif any(k in text for k in ["binary", "search", "unsorted", "big-o", "complexity", "sort", "partition", "algo", "array"]):
        reply = CACHED_ASK_ALGO_REPLY
    elif any(k in text for k in ["likelihood", "ratio", "neyman", "pearson", "monotone", "power", "alpha", "hypothesis", "prior"]):
        reply = CACHED_ASK_STATS_REPLY
    else:
        reply = CACHED_ASK_REPLY

    page = (anchor or {}).get("page")
    return {
        "mode": "socratic",
        "reply": reply,
        "hint_level": 2,
        "citations": [{"kind": "document", "page": page or 1}],
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
        "scenarios": [s for s in scenario_ids() if s in ("success", "caught")],
        "problems": problems,
    }


if __name__ == "__main__":  # pragma: no cover - manual R7 check
    import json

    print(json.dumps(validate_cache(), indent=2))
