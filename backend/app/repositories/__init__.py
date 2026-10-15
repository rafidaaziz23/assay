"""Repository layer for the Assay backend (DEV 2 breakdown section 4.1).

Every endpoint talks to these interfaces, never to a bare dict, so the in-memory
implementation used in dev/tests can be swapped for Firestore (``firestore.py``)
without touching a single handler. The Firestore port is deliberately a stub until
the schema in DEV 2 section 3 is ACC'd by DEV 1 and DEV 3.

Shapes follow the Firestore sketch in DEV 2 section 3:
``sessions/{sid}``, ``sessions/{sid}/checklist/{item_id}``,
``sessions/{sid}/chapters/{cid}``, ``.../turns/{turn_index}``,
``.../focus_events/{event_id}``, plus global ``catalog``/``cache`` collections.
"""
from __future__ import annotations

import time
import uuid
from typing import Any, Dict, List, Optional, Protocol


# ── interfaces ─────────────────────────────────────────────────────────────────

class SessionStore(Protocol):
    def create_session(self, session_id: str, **fields: Any) -> Dict[str, Any]: ...
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]: ...
    def update_session(self, session_id: str, **fields: Any) -> Optional[Dict[str, Any]]: ...


class ChapterStore(Protocol):
    def put_chapter(self, chapter: Dict[str, Any]) -> Dict[str, Any]: ...
    def get_chapter(self, chapter_id: str) -> Optional[Dict[str, Any]]: ...
    def session_chapters(self, session_id: str) -> List[Dict[str, Any]]: ...


class InterviewStore(Protocol):
    def create_interview(self, **fields: Any) -> Dict[str, Any]: ...
    def get_interview(self, interview_id: str) -> Optional[Dict[str, Any]]: ...


def _now_ms() -> int:
    return int(time.time() * 1000)


def new_id(prefix: str, width: int = 6) -> str:
    """Session/interview/appeal ids share one shape: ``<prefix>_<hex>``."""
    return f"{prefix}_{uuid.uuid4().hex[:width]}"


# ── in-memory implementation ───────────────────────────────────────────────────

class InMemoryStore:
    """Dev/test backend store.

    Chapter ids are the engine's ids (``ch_01``) and are therefore global rather
    than namespaced per session: the product is a single-user demo (PRD section 8,
    "Auth kompleks / multi-user" is a non-goal). Documented limitation, not a bug.
    """

    def __init__(self) -> None:
        self.reset()

    def reset(self) -> None:
        self.sessions: Dict[str, Dict[str, Any]] = {}
        self.chapters: Dict[str, Dict[str, Any]] = {}
        self.interviews: Dict[str, Dict[str, Any]] = {}
        self.focus_events: Dict[str, List[Dict[str, Any]]] = {}
        self.focus_flags: Dict[str, str] = {}
        self.ask_interactions: Dict[str, List[Dict[str, Any]]] = {}
        self.appeals: Dict[str, Dict[str, Any]] = {}
        self.calibrations: Dict[str, Dict[str, Any]] = {}
        self.grounding_cache: Dict[str, Dict[str, Any]] = {}
        self.demo_cache: Dict[str, Dict[str, Any]] = {}

    # ── sessions ──────────────────────────────────────────────────────────────
    def create_session(self, session_id: str, **fields: Any) -> Dict[str, Any]:
        record = {
            "session_id": session_id,
            "intent": "",
            "role": "",
            "role_is_custom": False,
            "custom_role": None,
            "suggested_others": False,
            "has_document": False,
            "source_mode": "role_taxonomy_generated",
            "demo_mode": "live",
            "status": "INTAKE",
            "checklist": [],
            "selected_item_ids": [],
            "syllabus_id": None,
            "syllabus_title": None,
            "doc_index": None,
            "document_name": None,
            "created_at": _now_ms(),
            "updated_at": _now_ms(),
            **fields,
        }
        self.sessions[session_id] = record
        return record

    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        return self.sessions.get(session_id)

    def update_session(self, session_id: str, **fields: Any) -> Optional[Dict[str, Any]]:
        record = self.sessions.get(session_id)
        if record is None:
            return None
        record.update(fields)
        record["updated_at"] = _now_ms()
        return record

    # ── checklist (subcollection sessions/{sid}/checklist) ────────────────────
    def set_checklist(self, session_id: str, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        session = self.sessions.get(session_id)
        if session is None:
            return []
        session["checklist"] = [dict(i) for i in items]
        session["selected_item_ids"] = [i["item_id"] for i in items if i.get("selected")]
        self.update_session(session_id, status="CHECKLIST")
        return session["checklist"]

    def apply_checklist_selection(self, session_id: str, selected_ids: List[str]) -> List[Dict[str, Any]]:
        """Rewrite the ``selected`` flag; only selected items feed the syllabus (F2)."""
        session = self.sessions.get(session_id)
        if session is None:
            return []
        wanted = set(selected_ids or [])
        for item in session.get("checklist", []):
            item["selected"] = item["item_id"] in wanted
        session["selected_item_ids"] = [
            i["item_id"] for i in session.get("checklist", []) if i.get("selected")
        ]
        self.update_session(session_id, status="CHECKLIST")
        return [i for i in session["checklist"] if i.get("selected")]

    def selected_checklist_items(self, session_id: str) -> List[Dict[str, Any]]:
        session = self.sessions.get(session_id) or {}
        return [i for i in session.get("checklist", []) if i.get("selected")]

    # ── chapters (subcollection sessions/{sid}/chapters) ──────────────────────
    def put_chapter(self, chapter: Dict[str, Any]) -> Dict[str, Any]:
        record = dict(chapter)
        record.setdefault("status", "LOCKED")
        record.setdefault("next_locked", True)
        record.setdefault("content_markdown", "")
        record.setdefault("references", [])
        record.setdefault("source_pages", [])
        record.setdefault("prerequisites", [])
        record.setdefault("pages", [])
        record.setdefault("score", {})
        record.setdefault("calibration", None)
        record.setdefault("integrity_flag", "clean")
        record.setdefault("honeypot_verdict", None)
        record.setdefault("verifier", None)
        record.setdefault("focus_summary", None)
        record.setdefault("interview_id", None)
        record.setdefault("pass_history", [])
        self.chapters[record["chapter_id"]] = record
        return record

    def get_chapter(self, chapter_id: str) -> Optional[Dict[str, Any]]:
        return self.chapters.get(chapter_id)

    def update_chapter(self, chapter_id: str, **fields: Any) -> Optional[Dict[str, Any]]:
        chapter = self.chapters.get(chapter_id)
        if chapter is None:
            return None
        chapter.update(fields)
        return chapter

    def session_chapters(self, session_id: str) -> List[Dict[str, Any]]:
        rows = [c for c in self.chapters.values() if c.get("session_id") == session_id]
        return sorted(rows, key=lambda c: c.get("order", 0))

    def next_chapter(self, chapter_id: str) -> Optional[Dict[str, Any]]:
        chapter = self.chapters.get(chapter_id)
        if chapter is None:
            return None
        order = chapter.get("order", 0) + 1
        for row in self.chapters.values():
            if row.get("order") == order and row.get("session_id") == chapter.get("session_id"):
                return row
        return None

    def previous_chapter(self, chapter_id: str) -> Optional[Dict[str, Any]]:
        chapter = self.chapters.get(chapter_id)
        if chapter is None:
            return None
        order = chapter.get("order", 0) - 1
        if order < 1:
            return None
        for row in self.chapters.values():
            if row.get("order") == order and row.get("session_id") == chapter.get("session_id"):
                return row
        return None

    def set_chapter_status(self, chapter_id: str, new_status: str) -> Optional[Dict[str, Any]]:
        chapter = self.chapters.get(chapter_id)
        if chapter is None:
            return None
        chapter["status"] = new_status
        return chapter

    def refresh_next_locked(self, chapter_id: str) -> bool:
        """``next_locked`` is stored on the chapter, never computed per request.

        DEV 2 section 3 reason 4: recomputing at read time races when two events
        land together and the gate can leak. Last chapter has nothing to lock.

        "Locked" means the successor is still ``LOCKED``. API-CONTRACTS section 2.4
        words it as "until the next chapter is UNLOCKED", but ``apply_score`` moves the
        successor to ``ACTIVE_READING`` when a chapter passes — under the literal
        reading the gate would never open and the demo would dead-end at chapter 1.
        The status that unlocks the gate is therefore "no longer LOCKED".
        """
        chapter = self.chapters.get(chapter_id)
        if chapter is None:
            return False
        nxt = self.next_chapter(chapter_id)
        locked = bool(nxt) and nxt.get("status") == "LOCKED"
        chapter["next_locked"] = locked
        return locked

    # ── interviews (subcollection .../turns) ──────────────────────────────────
    def create_interview(self, interview_id: str, **fields: Any) -> Dict[str, Any]:
        record = {
            "interview_id": interview_id,
            "chapter_id": "",
            "session_id": "",
            "turn_index": 1,
            "turns": [],
            "running_score": 0,
            "is_concluded": False,
            "injected_term": None,
            "honeypot_metadata": None,
            "finalized": False,
            "created_at": _now_ms(),
            **fields,
        }
        self.interviews[interview_id] = record
        return record

    def get_interview(self, interview_id: str) -> Optional[Dict[str, Any]]:
        return self.interviews.get(interview_id)

    def add_interview_turn(self, interview_id: str, turn: Dict[str, Any]) -> Dict[str, Any]:
        """Append a turn to the interview's history.

        One entry per turn, written to the interview document. The Firestore port will
        spread these across ``.../turns/{turn_index}`` — a single hot document would hit
        the per-document write ceiling exactly during a live demo (DEV 2 section 3).
        """
        interview = self.interviews.get(interview_id)
        if interview is None:
            return {}
        interview.setdefault("turns", []).append({"at_ms": _now_ms(), **turn})
        return interview["turns"][-1]

    def get_interview_turns(self, interview_id: str) -> List[Dict[str, Any]]:
        interview = self.interviews.get(interview_id) or {}
        return list(interview.get("turns", []))

    def update_interview(self, interview_id: str, **fields: Any) -> Optional[Dict[str, Any]]:
        record = self.interviews.get(interview_id)
        if record is None:
            return None
        record.update(fields)
        return record

    # ── focus events (subcollection .../focus_events) ─────────────────────────
    def add_focus_events(self, interview_id: str, events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        bucket = self.focus_events.setdefault(interview_id, [])
        bucket.extend(dict(e) for e in events)
        return bucket

    def get_focus_events(self, interview_id: str) -> List[Dict[str, Any]]:
        return list(self.focus_events.get(interview_id, []))

    def set_focus_flag(self, interview_id: str, flag: str) -> None:
        self.focus_flags[interview_id] = flag

    def get_focus_flag(self, interview_id: str) -> Optional[str]:
        return self.focus_flags.get(interview_id)

    # ── audit trail: select-word ask (F7/F8) ──────────────────────────────────
    def add_ask_interaction(self, chapter_id: str, record: Dict[str, Any]) -> Dict[str, Any]:
        entry = {"at_ms": _now_ms(), **record}
        self.ask_interactions.setdefault(chapter_id, []).append(entry)
        return entry

    def get_ask_interactions(self, chapter_id: str) -> List[Dict[str, Any]]:
        return list(self.ask_interactions.get(chapter_id, []))

    # ── calibration (F14) ─────────────────────────────────────────────────────
    def save_calibration(self, chapter_id: str, record: Dict[str, Any]) -> Dict[str, Any]:
        """One calibration per chapter: a second submit is a correction, not a new row.

        ``predicted_score`` is taken BEFORE the reveal, so keeping the first answer would
        mean a student could re-guess after seeing the score and the gap would be
        meaningless. The latest submission wins, and the response says so.
        """
        entry = {"at_ms": _now_ms(), **record}
        self.calibrations[chapter_id] = entry
        chapter = self.chapters.get(chapter_id)
        if chapter is not None:
            chapter["calibration"] = entry
        return entry

    def get_calibration(self, chapter_id: str) -> Optional[Dict[str, Any]]:
        return self.calibrations.get(chapter_id)

    # ── appeals (F15) ─────────────────────────────────────────────────────────
    def save_appeal(self, appeal_id: str, record: Dict[str, Any]) -> Dict[str, Any]:
        entry = {"at_ms": _now_ms(), **record}
        self.appeals[appeal_id] = entry
        return entry

    def get_appeal(self, appeal_id: str) -> Optional[Dict[str, Any]]:
        return self.appeals.get(appeal_id)


_store: Optional[InMemoryStore] = None


def get_store() -> InMemoryStore:
    """Process-wide store singleton (endpoints and state machine share it)."""
    global _store
    if _store is None:
        _store = InMemoryStore()
    return _store
