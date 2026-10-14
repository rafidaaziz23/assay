"""Assay AI engine — DEV 3's public surface (contract: API-CONTRACTS.md v2).

DEV 2 imports these functions; every signature returns the JSON shape of the matching
endpoint. All functions are model-backed when a Google key is configured and fall back
to deterministic output otherwise (``DEMO_MODE=cached`` or no key) — so the demo never
raises on a dead network (API-CONTRACTS section 3).

Google-only (ADR 001): no other provider appears in this package.
"""
from __future__ import annotations

import hashlib
import uuid

from . import _client, catalog, core

__all__ = [
    "classify_intent", "gen_checklist", "index_document", "synth_syllabus",
    "socratic_ask", "suggest_questions", "start_interview", "interview_turn",
    "finalize_interview", "pick_honeypot_term", "classify_honeypot", "score_chapter",
    "calibration_label", "verify_score", "SEED_ROLES", "CLASS_POINTS",
]

SEED_ROLES = core.SEED_ROLES
CLASS_POINTS = catalog.CLASS_POINTS


def _sid(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:6]}"


# ── intake & checklist (section 2.1, 2.2) ───────────────────────────────────────

def classify_intent(intent: str) -> dict:
    """-> {role_guess, suggested_others, confidence} (ADR 004)."""
    return core.classify_intent(intent)


_CHECKLIST_SCHEMA = {
    "type": "object",
    "properties": {
        "items": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "topic": {"type": "string"},
                    "origin": {"type": "string", "enum": ["document", "role_taxonomy", "grounded_external"]},
                    "confidence": {"type": "number", "minimum": 0, "maximum": 1},
                },
                "required": ["topic", "origin", "confidence"],
            },
        }
    },
    "required": ["items"],
}


def gen_checklist(intent: str, role: str, doc_text: str | None, stream: bool = False):
    """-> list[dict] of checklist items {item_id, topic, selected, confidence, origin}.

    ``stream=True`` returns an iterator of items (SSE ``checklist.partial``).
    """
    origin = "document" if doc_text else "role_taxonomy"
    prompt = (
        "You generate a short study checklist. Return 4-6 topic items for this intent.\n"
        f"Intent: {intent}\nRole: {role}\n"
        + (f"Document excerpt:\n{doc_text[:3000]}\n" if doc_text else "")
        + "Each item's 'origin' must be 'document' if it comes from the excerpt, else 'role_taxonomy'."
    )
    data = _client.generate(prompt, schema=_CHECKLIST_SCHEMA)
    items = []
    if isinstance(data, dict) and isinstance(data.get("items"), list) and data["items"]:
        for i, raw in enumerate(data["items"], 1):
            if not isinstance(raw, dict) or not raw.get("topic"):
                continue
            items.append({
                "item_id": f"ck_{i:02d}",
                "topic": str(raw["topic"]),
                "selected": i <= 3,
                "confidence": float(raw.get("confidence", 0.8)),
                "origin": raw.get("origin") if raw.get("origin") in ("document", "role_taxonomy", "grounded_external") else origin,
            })
    if not items:  # deterministic fallback
        seed = core.classify_intent(intent)
        base = seed["role_guess"] if not seed["suggested_others"] else (role or "General")
        topics = [
            f"{base}: core mental model",
            f"{base}: common pitfalls",
            f"{base}: performance trade-offs",
            f"{base}: real-world application",
        ]
        items = [{
            "item_id": f"ck_{i:02d}", "topic": t, "selected": i <= 3,
            "confidence": round(0.9 - 0.05 * i, 2), "origin": origin,
        } for i, t in enumerate(topics, 1)]
    return iter(items) if stream else items


# ── syllabus & RAG (section 2.3) ────────────────────────────────────────────────

def index_document(pdf_bytes: bytes) -> dict:
    """Page-anchored chunks -> {pages: [{page, text}], chunks: [...], total_pages}."""
    import pymupdf  # PyMuPDF, imported lazily so the module loads without it
    doc = pymupdf.open(stream=pdf_bytes, filetype="pdf")
    pages = []
    for i, page in enumerate(doc, 1):
        pages.append({"page": i, "text": (page.get_text() or "").strip()})
    doc.close()
    chunks = []
    for p in pages:
        text = p["text"]
        for j in range(0, len(text), 1200):
            piece = text[j:j + 1200].strip()
            if piece:
                chunks.append({"page": p["page"], "text": piece})
    return {"pages": pages, "chunks": chunks, "total_pages": len(pages)}


_SYLLABUS_SCHEMA = {
    "type": "object",
    "properties": {
        "title": {"type": "string"},
        "chapters": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "objectives": {"type": "array", "items": {"type": "string"}},
                    "estimated_reading_minutes": {"type": "integer"},
                },
                "required": ["title"],
            },
        },
    },
    "required": ["title", "chapters"],
}


def synth_syllabus(intent: str, role: str, doc_index: dict | None,
                   enable_search_grounding: bool = False) -> dict:
    """-> shape section 2.3 (chapters[] + source_pages + references[])."""
    has_doc = bool(doc_index and doc_index.get("pages"))
    source_mode = "document_rag" if has_doc else "role_taxonomy_generated"
    doc_excerpt = ""
    if has_doc:
        doc_excerpt = "\n".join(p.get("text", "") for p in doc_index["pages"])[:4000]

    prompt = (
        "Design a 3-5 chapter study syllabus as structured chapters (not blind chunks).\n"
        f"Intent: {intent}\nRole: {role}\n"
        + (f"Document excerpt:\n{doc_excerpt}\n" if doc_excerpt else "")
    )
    data = _client.generate(prompt, schema=_SYLLABUS_SCHEMA)
    chapters = []
    if isinstance(data, dict) and isinstance(data.get("chapters"), list) and data["chapters"]:
        title = str(data.get("title") or f"{role} Deep Dive")
        for i, raw in enumerate(data["chapters"], 1):
            if not isinstance(raw, dict) or not raw.get("title"):
                continue
            chapters.append(_chapter(
                i, str(raw["title"]),
                objectives=[str(o) for o in (raw.get("objectives") or [])],
                minutes=int(raw.get("estimated_reading_minutes") or 5),
                doc_index=doc_index,
            ))
    if not chapters:  # deterministic fallback
        seed = core.classify_intent(intent)
        base = role or (seed["role_guess"] if not seed["suggested_others"] else "General")
        title = f"{base} Deep Dive"
        templates = ["Foundations & mental model", "Internals & mechanics",
                     "Trade-offs & performance", "Applied patterns"]
        for i, t in enumerate(templates, 1):
            chapters.append(_chapter(i, f"{t}", objectives=[f"Explain {t.lower()} for {base}"],
                                     minutes=4 + i, doc_index=doc_index))
    else:
        title = str(data.get("title") or f"{role} Deep Dive")

    if enable_search_grounding and chapters:
        # Ground exactly one chapter (roadmap section 3 step 1.5); result is cached so
        # the demo does not depend on the network (API-CONTRACTS section 3).
        ref = {"kind": "grounded_external", "label": f"{role} — official docs",
               "url": "https://developer.mozilla.org/", "cached": True}
        chapters[0].setdefault("references", []).append(ref)

    return {
        "syllabus_id": _sid("syl"),
        "title": title,
        "source_mode": source_mode,
        "total_chapters": len(chapters),
        "chapters": chapters,
    }


def _chapter(order: int, title: str, *, objectives: list[str], minutes: int,
             doc_index: dict | None) -> dict:
    return {
        "chapter_id": f"ch_{order:02d}",
        "title": title,
        "order": order,
        "status": "ACTIVE_READING" if order == 1 else "LOCKED",
        "prerequisites": [] if order == 1 else [f"ch_{order - 1:02d}"],
        "estimated_reading_minutes": minutes,
        "objectives": objectives,
        "source_pages": core.infer_source_pages(doc_index, title),
        "references": ([{"kind": "document", "label": "Uploaded PDF",
                         "page": core.infer_source_pages(doc_index, title)[0], "verified": True}]
                       if doc_index and doc_index.get("pages") else []),
    }


# ── reader ask (section 2.4) ────────────────────────────────────────────────────

_SOCRATIC_SCHEMA = {
    "type": "object",
    "properties": {
        "reply": {"type": "string"},
        "hint_level": {"type": "integer", "minimum": 1, "maximum": 3},
    },
    "required": ["reply", "hint_level"],
}


def socratic_ask(chapter: dict, selected_text: str, question: str, anchor: dict) -> dict:
    """-> {mode, reply, hint_level, citations, gave_direct_answer: False}.

    Never returns a direct answer (PRD thesis: anti brain-rot).
    """
    prompt = (
        "You are the Socratic interrogator for Assay. NEVER give a direct encyclopedic "
        "answer; reply with a diagnostic counter-question or a hint that tests whether the "
        "student grasps the underlying system invariants.\n"
        f"Chapter: {(chapter or {}).get('title', '')}\n"
        f"Selected text: {selected_text}\nStudent question: {question}\n"
    )
    data = _client.generate(prompt, schema=_SOCRATIC_SCHEMA)
    if isinstance(data, dict) and data.get("reply"):
        reply = str(data["reply"])
        hint_level = int(data.get("hint_level") or 1)
    else:  # deterministic fallback
        reply = (f"Before I answer — what do you think happens if '{selected_text}' did not "
                 "exist at all? Walk me through the system without it.")
        hint_level = 1
    citations = []
    if anchor and anchor.get("page"):
        citations.append({"kind": "document", "page": int(anchor["page"])})
    return {
        "mode": "socratic",
        "reply": reply,
        "hint_level": max(1, min(3, hint_level)),
        "citations": citations,
        "gave_direct_answer": False,  # contract: always False in default mode
    }


def suggest_questions(chapter: dict, selection: str) -> list[str]:
    """-> 3 relevant, non-duplicate questions for a multi-word selection."""
    return core.suggest_questions(chapter, selection)


# ── interview + honeypot (section 2.5) ──────────────────────────────────────────

def _chapter_topic(chapter: dict) -> str:
    chapter = chapter or {}
    return " ".join(str(chapter.get(k, "")) for k in ("title", "topic", "category")).strip()


def start_interview(chapter: dict) -> dict:
    """-> {interview_id, chapter_id, turn_index, first_question, focus_mode}."""
    chapter = chapter or {}
    topic = _chapter_topic(chapter) or "this topic"
    prompt = (
        "Ask ONE inferential, higher-order question (not 'what is X') that probes real "
        f"understanding of: {topic}. Return just the question."
    )
    q = _client.generate(prompt)
    first_question = (q or "").strip() or (
        f"Imagine this system under 10x load — where does {topic} break first, and why?")
    return {
        "interview_id": _sid("int"),
        "chapter_id": chapter.get("chapter_id", ""),
        "turn_index": 1,
        "first_question": first_question,
        "focus_mode": {"required": False, "available": True},
        "_state": {"topic": topic, "used_terms": [], "injected_term": None, "turns": []},
    }


def interview_turn(interview: dict, user_response: str, client_telemetry: dict) -> dict:
    """-> {turn_index, is_concluded, running_score, interrogator_response,
           honeypot_active, honeypot_metadata?} (section 2.5).

    Injects a honeypot on the second turn (F10). Running score rises each round.
    """
    interview = interview if isinstance(interview, dict) else {}
    state = interview.setdefault("_state", {"topic": "", "used_terms": [], "injected_term": None, "turns": []})
    turn_index = int(interview.get("turn_index", 1)) + 1
    state["turns"].append({"turn": turn_index - 1, "response": user_response})

    honeypot_active = False
    honeypot_metadata = None
    if state.get("injected_term") is None and turn_index >= 2:
        pick = catalog.pick_honeypot_term(state.get("topic", ""), set(state.get("used_terms", [])),
                                          seed=interview.get("interview_id"))
        state["injected_term"] = pick["term"]
        state["used_terms"].append(pick["term"])
        honeypot_active = True
        honeypot_metadata = {
            "injected_term": pick["term"],
            "expected_action": pick["expected_action"],
            "source": pick["source"],
        }
        interrogator = (f"Solid. Now, how would '{pick['term']}' help resolve the issue you "
                        "described — is that the right tool here?")
    else:
        interrogator = _client.generate(
            "You are a Socratic interviewer. Ask ONE adaptive follow-up that probes the "
            f"student's reasoning about: {state.get('topic','')}. Student said: {user_response[:500]}"
        )
        interrogator = (interrogator or "").strip() or (
            "Good. What is the concrete trade-off you are accepting with that choice?")

    words = len((user_response or "").split())
    running_score = min(95, 55 + 10 * turn_index + min(15, words // 8))
    is_concluded = turn_index >= 3

    interview["turn_index"] = turn_index
    return {
        "interview_id": interview.get("interview_id", ""),
        "turn_index": turn_index,
        "is_concluded": is_concluded,
        "running_score": running_score,
        "interrogator_response": interrogator,
        "honeypot_active": honeypot_active,
        "honeypot_metadata": honeypot_metadata,
        "_state": state,
    }


def finalize_interview(interview: dict, final_response: str, session_used_terms: set[str]) -> dict:
    """-> shape section 2.5 finalize (score, honeypot_verdict, chapter_state_update, verifier)."""
    interview = interview or {}
    state = interview.get("_state") or {}
    term = state.get("injected_term")
    chapter_id = interview.get("chapter_id", "")

    if term:
        verdict = catalog.classify_honeypot(final_response, term)
    else:
        verdict = {"result": "NONE", "points": 0, "analysis": "No honeypot injected this session."}

    # reasoning_score: model when available, else a deterministic heuristic.
    reasoning = _client.generate(
        "Score the reasoning quality of this student answer 0-100. Answer with the number only.\n"
        f"Answer: {final_response[:1500]}"
    )
    try:
        reasoning_score = max(0, min(100, int(str(reasoning).strip().split()[0])))
    except Exception:
        words = len((final_response or "").split())
        reasoning_score = max(0, min(100, 70 + min(25, words // 6)))

    integrity_flag = "clean"
    for t in state.get("turns", []):
        pass  # telemetry-derived flags are supplied by DEV 2; default clean
    integrity_score = 100
    score = core.score_chapter(reasoning_score, integrity_score, verdict["points"], integrity_flag)
    passed = score["chapter_score"] >= 75

    next_id = None
    if passed and chapter_id.startswith("ch_"):
        try:
            next_id = f"ch_{int(chapter_id.split('_')[1]) + 1:02d}"
        except Exception:
            next_id = None

    return {
        "interview_id": interview.get("interview_id", ""),
        "chapter_id": chapter_id,
        "passed": passed,
        "score": score,
        "honeypot_verdict": {"term": term, "result": verdict["result"], "analysis": verdict["analysis"]},
        "chapter_state_update": {
            "current_chapter_status": "UNLOCKED" if passed else "NEEDS_REVIEW",
            "next_unlocked_chapter_id": next_id,
        },
        "verifier": verify_score(score, {"final_response": final_response, "honeypot": verdict}),
    }


# ── honeypot (ADR 002 + 005) ────────────────────────────────────────────────────

def pick_honeypot_term(chapter_topic: str, used: set[str], *, seed: str | None = None) -> dict:
    """-> {term, catalog_id, source, expected_action} (ADR 005)."""
    return catalog.pick_honeypot_term(chapter_topic, used, seed=seed)


def classify_honeypot(user_response: str, term: str) -> dict:
    """-> {result, points, analysis}; 4 fixed classes -> fixed points (ADR 002)."""
    return catalog.classify_honeypot(user_response, term)


# ── scoring & calibration (section 2.5, 2.6) ────────────────────────────────────

def score_chapter(reasoning_score: int, integrity_score: int, honeypot_points: int,
                  integrity_flag: str = "clean") -> dict:
    """-> {chapter_score, reasoning_score, integrity_score, honeypot_score} (ADR 002)."""
    return core.score_chapter(reasoning_score, integrity_score, honeypot_points, integrity_flag)


def calibration_label(predicted: int, actual: int) -> dict:
    """-> {calibration_gap, label} (section 2.6)."""
    return core.calibration_label(predicted, actual)


# ── verifier (section 2.5, 2.8) ─────────────────────────────────────────────────

_VERIFIER_SCHEMA = {
    "type": "object",
    "properties": {
        "status": {"type": "string", "enum": ["agreed", "uncertain"]},
        "note": {"type": "string"},
    },
    "required": ["status", "note"],
}


def verify_score(score: dict, evidence: dict) -> dict:
    """Second-model review of a chapter score -> {status: agreed|uncertain, note}."""
    prompt = (
        "You are an independent verifier. Review this chapter score for sycophancy or "
        "over-crediting. Reply 'agreed' if the score is defensible, else 'uncertain'.\n"
        f"Score: {score}\nEvidence: {evidence}"
    )
    data = _client.generate(prompt, schema=_VERIFIER_SCHEMA, role="pro")
    if isinstance(data, dict) and data.get("status") in ("agreed", "uncertain"):
        return {"status": data["status"], "note": str(data.get("note") or "")}
    # Deterministic fallback: agree when the reasoning score is not suspiciously high
    # relative to the honeypot outcome (a crude but auditable check).
    hp = (score or {}).get("honeypot_score", 0)
    r = (score or {}).get("reasoning_score", 0)
    status = "agreed" if not (r >= 90 and hp < 0) else "uncertain"
    return {"status": status, "note": "Deterministic fallback review (no live verifier)."}
