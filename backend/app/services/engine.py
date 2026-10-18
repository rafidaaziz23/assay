"""Boundary between the backend and the DEV 3 AI engine (repo-root ``ai/`` package).

Folder ownership (WBS section 6.6): DEV 2 owns ``backend/``, DEV 3 owns ``ai/``.
Backend may *read* ``ai/`` but must not write it. This module is the single place the
import happens, so:

* the path juggling lives in one file instead of every endpoint;
* if the engine is unavailable, every helper degrades to its deterministic shape
  rather than raising — DEMO-SCRIPT golden rule 1, "no blank spinners, ever".
"""
from __future__ import annotations

import sys
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

_REPO_ROOT = Path(__file__).resolve().parents[3]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

try:  # pragma: no cover - only the import guard is environment dependent
    import ai as _engine  # type: ignore

    ENGINE_AVAILABLE = True
except Exception:  # pragma: no cover
    _engine = None  # type: ignore
    ENGINE_AVAILABLE = False

ENGINE_ROOT = _REPO_ROOT


class _Unavailable:
    """Deterministic stand-in used only when the engine package cannot be imported."""

    SEED_ROLES = [
        "Frontend", "Backend", "Fullstack", "DevOps", "Data/ML",
        "Mobile", "QA/Test", "Security", "System Design",
    ]
    CLASS_POINTS = {
        "CRITICAL_REJECTION": 2,
        "AI_HALLUCINATION_COPYPASTE": -2,
        "UNVERIFIED_HONEST": 0,
        "EVASIVE": -1,
    }

    @staticmethod
    def classify_intent(intent: str) -> Dict[str, Any]:
        return {"role_guess": "Others", "suggested_others": True, "confidence": 0.4}

    @staticmethod
    def gen_checklist(intent: str, role: str, doc_text: Optional[str], stream: bool = False):
        items = [
            {"item_id": f"ck_{i:02d}", "topic": f"{role or 'General'}: topic {i}",
             "selected": i <= 3, "confidence": 0.8,
             "origin": "document" if doc_text else "role_taxonomy"}
            for i in range(1, 5)
        ]
        return iter(items) if stream else items

    @staticmethod
    def index_document(pdf_bytes: bytes) -> Dict[str, Any]:
        """Offline ingest: one page, honestly labelled (never invents pagination)."""
        return {"pages": [{"page": 1, "text": ""}], "chunks": [], "total_pages": 1}

    @staticmethod
    def synth_syllabus(intent: str, role: str, doc_index: Optional[dict], enable_search_grounding: bool = False):
        chapters = [
            {"chapter_id": f"ch_{i:02d}", "title": f"{role or 'General'} chapter {i}",
             "order": i, "status": "ACTIVE_READING" if i == 1 else "LOCKED",
             "prerequisites": [] if i == 1 else [f"ch_{i - 1:02d}"],
             "estimated_reading_minutes": 5, "source_pages": [], "references": []}
            for i in range(1, 4)
        ]
        return {"syllabus_id": "syl_offline", "title": f"{role or 'General'} Deep Dive",
                "source_mode": "role_taxonomy_generated", "total_chapters": len(chapters),
                "chapters": chapters}

    @staticmethod
    def socratic_ask(chapter: dict, selected_text: str, question: str, anchor: dict) -> Dict[str, Any]:
        return {"mode": "socratic",
                "reply": f"Before I answer — what breaks if '{selected_text}' did not exist?",
                "hint_level": 1, "citations": [], "gave_direct_answer": False}

    @staticmethod
    def suggest_questions(chapter: dict, selection: str) -> List[str]:
        return [f"What breaks without {selection}?",
                f"What does {selection} trade off?",
                f"Where does {selection} bottleneck?"]

    @staticmethod
    def calibration_label(predicted: int, actual: int) -> Dict[str, Any]:
        gap = int(predicted) - int(actual)
        label = "overconfident" if gap > 15 else "underconfident" if gap < -15 else "well_calibrated"
        return {"calibration_gap": gap, "label": label}

    # ── interview + score inputs the engine does not own ──

    @staticmethod
    def pick_honeypot_term(chapter_topic: str, used: set, *, seed: Optional[str] = None) -> Dict[str, Any]:
        """Offline term rotation (the live path is ``ai.catalog``)."""
        term = "React Quantum Hook"
        if _FALLBACK_HONEYPOT_KEYWORDS in (chapter_topic or "").lower():
            term = "Zero-Latency Mutex"
        return {"term": term, "catalog_id": "hp_offline", "category": "General",
                "source": "deterministic_catalog",
                "expected_action": "REJECT_AS_FICTITIOUS"}

    @staticmethod
    def start_interview(chapter: dict) -> Dict[str, Any]:
        topic = (chapter or {}).get("title") or "this topic"
        return {
            "interview_id": "int_offline",
            "chapter_id": (chapter or {}).get("chapter_id", ""),
            "turn_index": 1,
            "first_question": (
                f"Imagine this system under 10x load — where does {topic} break first, "
                f"and what evidence would tell you it is that and not something else?"
            ),
            "focus_mode": {"required": False, "available": True},
        }

    @staticmethod
    def interview_follow_up(interview: dict, user_response: str, telemetry: Optional[dict]) -> str:
        return ("Good. What is the concrete trade-off you are accepting with that choice, "
                "and where would it stop being the right call?")

    @staticmethod
    def classify_honeypot(user_response: str, term: str) -> Dict[str, Any]:
        """Offline stand-in: the live classifier lives in ``ai/catalog.py`` (DEV 3)."""
        text = (user_response or "").lower()
        if "tidak ada" in text or "does not exist" in text or "fictional" in text:
            result = "CRITICAL_REJECTION"
        elif "i don't know" in text or "not sure" in text:
            result = "UNVERIFIED_HONEST"
        elif len(text.split()) > 10:
            result = "AI_HALLUCINATION_COPYPASTE"
        else:
            result = "EVASIVE"
        return {"result": result, "points": _Unavailable.CLASS_POINTS[result], "analysis": ""}

    @staticmethod
    def score_reasoning(final_response: str) -> int:
        words = len((final_response or "").split())
        return max(0, min(100, 70 + min(25, words // 6)))

    @staticmethod
    def verify_score(score: dict, evidence: dict) -> Dict[str, Any]:
        return {"status": "agreed", "note": "Deterministic fallback review (offline)."}

    @staticmethod
    def appeal(chapter_id: str, reason: str) -> Dict[str, Any]:
        """Offline appeal routing. Same shape as ``ai.appeal`` (section 2.8)."""
        return {
            "appeal_id": f"apl_{uuid.uuid4().hex[:4]}",
            "chapter_id": chapter_id,
            "status": "under_review",
            "reviewer": "verifier_model",
            "reason": reason,
            "possible_outcome": ["upheld", "score_revised", "re_interview"],
        }


_FALLBACK_HONEYPOT_KEYWORDS = "backend"


# ── helpers the engine does not (yet) expose ───────────────────────────────────
# ``ai/`` has no ``score_reasoning`` or ``interview_follow_up``. Rather than have the
# backend call methods that may not exist — an AttributeError in the middle of a demo is
# exactly the failure mode F17 exists to prevent — these two wrap the engine when it
# offers the capability and answer deterministically when it does not.

def reasoning_score(final_response: str) -> int:
    """0-100 reasoning quality of a final answer.

    Uses the engine when it exposes the capability; otherwise a word-count heuristic
    that is monotone in effort. Never the sole basis for a pass: the honeypot points and
    the integrity adjustment are folded in by ``core.scoring.chapter_score``.
    """
    fn = getattr(engine, "score_reasoning", None)
    if callable(fn):
        try:
            value = int(fn(final_response))
            return max(0, min(100, value))
        except Exception:
            pass
    words = len((final_response or "").split())
    return max(0, min(100, 70 + min(25, words // 6)))


def follow_up(interview: dict, user_response: str, telemetry: Optional[dict]) -> str:
    """Adaptive follow-up question for an interview turn.

    Engine-first, deterministic second. The fallback must ask about a trade-off rather
    than a definition — the fallback runs precisely when the live model is unavailable,
    which is when a weak question would be most visible.
    """
    for name in ("interview_follow_up", "follow_up_question"):
        fn = getattr(engine, name, None)
        if callable(fn):
            try:
                text = fn(interview, user_response, telemetry)
                if text:
                    return str(text)
            except Exception:
                pass
    # A pasted answer gets pushed on its reasoning rather than its wording.
    if telemetry and telemetry.get("paste_detected"):
        return ("Walk me through that again in your own words, and tell me which part you "
                "are least sure about.")
    topic = (interview or {}).get("chapter_id", "this topic")
    return (f"Good. What concrete trade-off are you accepting there — and at what point "
            f"would that choice stop being right for {topic}?")


# ── F7/F8 pass-throughs ────────────────────────────────────────────────────────
# Same reasoning as above: call the engine when it offers the capability, answer
# deterministically when it does not. Each wrapper returns the contract's shape either
# way, so the endpoint never has to branch on engine availability.

def socratic_ask(chapter: dict, selected_text: str, question: str, anchor: dict) -> Dict[str, Any]:
    """Select-word -> Socratic counter-inquiry (F7).

    The deterministic stand-in answers with a *question*, never an explanation: this path
    runs when the live model is unavailable, which is precisely when accidentally handing
    over the answer would be most obvious on camera.
    """
    for name in ("socratic_ask", "ask"):
        fn = getattr(engine, name, None)
        if callable(fn):
            try:
                result = fn(chapter, selected_text, question, anchor)
                if isinstance(result, dict) and result.get("reply"):
                    return result
            except Exception:
                pass
    page = (anchor or {}).get("page")
    where = f"on page {page}" if page else "in this chapter"
    return {
        "mode": "socratic",
        "reply": (
            f"You highlighted \"{(selected_text or '').strip()[:80]}\" {where} and asked: "
            f"\"{(question or '').strip()[:120]}\". Before I point anywhere — what do you "
            f"expect that phrase to do at runtime, and which part of your own answer would "
            f"break first under load?"
        ),
        "hint_level": 1,
        "citations": [{"kind": "document", "page": page}] if page else [],
        "gave_direct_answer": False,
    }


def suggest_questions(chapter: dict, selection: str) -> List[str]:
    """Three follow-up questions for a multi-word selection (F8)."""
    for name in ("suggest_questions", "suggestions"):
        fn = getattr(engine, name, None)
        if callable(fn):
            try:
                questions = list(fn(chapter, selection))
                if questions:
                    return questions
            except Exception:
                pass
    topic = (selection or "").strip()[:60] or "this passage"
    return [
        f"What does \"{topic}\" change about the runtime behaviour, and why?",
        f"Where would \"{topic}\" break first — and what evidence would show it?",
        f"Which trade-off does \"{topic}\" force you to accept?",
    ]


# A union rather than a bare module type: ``ai`` is a package when importable and
# ``_Unavailable`` otherwise, and every caller uses the same attribute surface.
Engine = Union[Any, _Unavailable]

engine: Engine = _engine if ENGINE_AVAILABLE else _Unavailable()
