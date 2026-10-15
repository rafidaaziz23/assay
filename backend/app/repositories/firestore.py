"""Firestore port for the repository interfaces (DEV 2 section 3 schema).

Status: STUB, intentionally. The Firestore schema in the DEV 2 breakdown is still
listed as "belum dibahas/ACC DEV 1 & DEV 3" (section 8, open questions), and the
vector-search limits are unverified. Building on that now would burn a full day of a
budget that has none (Hari 3 is already full).

What this file freezes today is the *contract*: the same method names as
``InMemoryStore``, so switching implementations is a one-line change in
``repositories/__init__.py`` rather than a handler refactor on Hari 2.

Nested layout it must implement once ACC'd:
    sessions/{sid}
      checklist/{item_id}
      chapters/{cid}            + pages/{page_no} + references/{ref_id}
                                + turns/{turn_index} + focus_events/{event_id}
    catalog/honeypots/{term_id}  (DEV 3 / ADR 005)
    cache/grounding/{topic_hash}, cache/demo/{scenario_id}
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from . import InMemoryStore


class FirestoreStore(InMemoryStore):
    """Placeholder that behaves like the in-memory store until Firestore is wired.

    Subclassing keeps every endpoint import-compatible (same method surface). Wiring
    the real client must preserve the write-spreading property the nested layout
    exists for: one hot document per turn/event would hit Firestore's ~1 write/s
    per-document ceiling exactly during the live demo.
    """

    def __init__(self, project_id: Optional[str] = None, client: Any = None) -> None:
        super().__init__()
        self.project_id = project_id
        self.client = client


def build_store(project_id: Optional[str] = None) -> InMemoryStore:
    """Factory: Firestore when configured and reachable, in-memory otherwise.

    Kept permissive on purpose — a demo must not fail to boot because the database
    is unreachable (DEMO-SCRIPT golden rule 1: no blank spinners, ever).
    """
    if not project_id:
        return InMemoryStore()
    try:  # noqa: SIM105 - probe only; falls back to memory on any failure
        from google.cloud import firestore  # type: ignore  # noqa: F401
    except Exception:
        return InMemoryStore()
    return FirestoreStore(project_id=project_id)
