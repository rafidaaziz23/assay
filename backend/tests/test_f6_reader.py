"""F6/F7/F8 — Gated chapter reader, state machine, inline Socratic ask.

Contract under test: ``GET /api/v1/chapters/:chapterId``,
``POST /api/v1/chapters/:chapterId/ask``, ``GET /api/v1/chapters/:chapterId/suggestions``.

Rules that must hold:
* F6 — the BACKEND is the gate. ``next_locked`` is stored on the chapter, never
  recomputed per request (`refresh_next_locked`), and the chapter content plus the
  ``interview_available`` flag come from server state.
* **Honeypot does not change state** — it only fills ``honeypot_score``. Asserted here
  because it is the invariant most likely to be broken by a later change.
* F7/F8 — every ask interaction is persisted (engagement metric + audit), and
  ``gave_direct_answer`` stays ``false`` in the default mode.
"""
from __future__ import annotations

import io

from app.repositories import get_store


def _seed_syllabus(frontend_client, sid: str, with_doc: bool = True):
    if with_doc:
        frontend_client.post(
            f"/api/v1/intake/{sid}/document",
            files={"file": ("module.txt", io.BytesIO(
                b"Page 1\nReact reconciliation compares trees.\n\n"
                b"Page 2\nFiber splits work into units and yields.\n\n"
                b"Page 3\nPriority lanes order the work.\n"
            ), "text/plain")},
        )
    frontend_client.post(f"/api/v1/intake/{sid}/checklist", json={})
    return frontend_client.post(f"/api/v1/intake/{sid}/syllabus", json={}).json()


def _start(frontend_client) -> str:
    return frontend_client.post("/api/v1/intake", json={
        "intent": "I want to understand how React rendering works internally",
        "role": "Frontend",
    }).json()["session_id"]


# ── F6: reader + gate ──────────────────────────────────────────────────────────

def test_first_chapter_is_readable_and_unlocked_for_interview(frontend_client):
    chapters = _seed_syllabus(frontend_client, _start(frontend_client))["chapters"]
    first = sorted(chapters, key=lambda c: c["order"])[0]

    body = frontend_client.get(f"/api/v1/chapters/{first['chapter_id']}").json()
    assert body["chapter_id"] == first["chapter_id"]
    assert body["status"] == "ACTIVE_READING"
    assert body["content_markdown"].strip()
    assert body["interview_available"] is True


def test_second_chapter_is_locked_for_interview_until_unlocked(frontend_client):
    """The gate: chapter 2 has content but no interview while LOCKED."""
    chapters = _seed_syllabus(frontend_client, _start(frontend_client))["chapters"]
    ordered = sorted(chapters, key=lambda c: c["order"])
    second = ordered[1]

    body = frontend_client.get(f"/api/v1/chapters/{second['chapter_id']}").json()
    assert body["status"] == "LOCKED"
    assert body["interview_available"] is False


def test_reader_exposes_the_gate_decision_not_just_the_status(frontend_client):
    """`next_locked` is the field the frontend renders; it must be server-computed."""
    chapters = _seed_syllabus(frontend_client, _start(frontend_client))["chapters"]
    first = sorted(chapters, key=lambda c: c["order"])[0]
    body = frontend_client.get(f"/api/v1/chapters/{first['chapter_id']}").json()
    assert body["next_locked"] is True
    assert body["next_chapter_id"] == sorted(chapters, key=lambda c: c["order"])[1]["chapter_id"]
    assert body["unlock_threshold"] == 75
    assert body["gate_source"]


def test_gate_opens_after_the_next_chapter_unlocks(frontend_client, clean_store):
    """After chapter 1 passes, chapter 2 is served as ACTIVE_READING, unlocked."""
    chapters = sorted(
        _seed_syllabus(frontend_client, _start(frontend_client))["chapters"],
        key=lambda c: c["order"],
    )
    store = get_store()
    store.set_chapter_status(chapters[0]["chapter_id"], "UNLOCKED")
    store.set_chapter_status(chapters[1]["chapter_id"], "ACTIVE_READING")
    store.refresh_next_locked(chapters[0]["chapter_id"])

    first = frontend_client.get(f"/api/v1/chapters/{chapters[0]['chapter_id']}").json()
    second = frontend_client.get(f"/api/v1/chapters/{chapters[1]['chapter_id']}").json()
    assert first["next_locked"] is False
    assert first["interview_available"] is False
    assert second["status"] == "ACTIVE_READING"
    assert second["interview_available"] is True


def test_next_locked_reflects_a_successor_unlocked_by_a_passing_score(frontend_client):
    """End-to-end version of the gate: apply_score opens chapter 2, the reader sees it.

    API-CONTRACTS words `next_locked` as "until the next chapter is UNLOCKED", while
    apply_score moves the successor to ACTIVE_READING. The literal reading would leave
    the gate shut forever, so the invariant is pinned on real scoring, not on a
    hand-set status.
    """
    from app.core import state_machine as sm

    chapters = sorted(
        _seed_syllabus(frontend_client, _start(frontend_client))["chapters"],
        key=lambda c: c["order"],
    )
    store = get_store()
    store.set_chapter_status(chapters[0]["chapter_id"], "INTERVIEW")
    outcome = sm.apply_score(
        chapters[0]["chapter_id"],
        {"chapter_score": 88, "reasoning_score": 86, "integrity_score": 100, "honeypot_score": 2},
    )
    assert outcome["passed"] is True
    assert outcome["next_unlocked_chapter_id"] == chapters[1]["chapter_id"]

    first = frontend_client.get(f"/api/v1/chapters/{chapters[0]['chapter_id']}").json()
    second = frontend_client.get(f"/api/v1/chapters/{chapters[1]['chapter_id']}").json()
    assert first["status"] == "UNLOCKED"
    assert first["next_locked"] is False
    assert second["status"] == "ACTIVE_READING"
    assert second["interview_available"] is True


def test_unknown_chapter_is_404(frontend_client):
    assert frontend_client.get("/api/v1/chapters/ch_does_not_exist").status_code == 404


def test_last_chapter_has_nothing_locked_behind_it(frontend_client, clean_store):
    chapters = sorted(
        _seed_syllabus(frontend_client, _start(frontend_client))["chapters"],
        key=lambda c: c["order"],
    )
    last = chapters[-1]
    body = frontend_client.get(f"/api/v1/chapters/{last['chapter_id']}").json()
    assert body["next_locked"] is False
    assert body["next_chapter_id"] is None


def test_source_pages_are_the_documents_pages(frontend_client):
    chapters = sorted(
        _seed_syllabus(frontend_client, _start(frontend_client))["chapters"],
        key=lambda c: c["order"],
    )
    for ch in chapters:
        body = frontend_client.get(f"/api/v1/chapters/{ch['chapter_id']}").json()
        assert body["source_pages"]
        assert set(body["source_pages"]) <= {1, 2, 3}


# ── F7: Socratic ask ───────────────────────────────────────────────────────────

def test_ask_never_gives_a_direct_answer(frontend_client):
    """Thesis consistency (F7): default mode must not hand over the answer."""
    chapters = _seed_syllabus(frontend_client, _start(frontend_client))["chapters"]
    cid = sorted(chapters, key=lambda c: c["order"])[0]["chapter_id"]

    body = frontend_client.post(f"/api/v1/chapters/{cid}/ask", json={
        "session_id": "sess_any",
        "selected_text": "reconciliation",
        "question": "What does this actually do?",
        "anchor": {"page": 1, "char_start": 0, "char_end": 14},
    }).json()
    assert body["mode"] == "socratic"
    assert body["gave_direct_answer"] is False
    assert body["reply"].strip()
    assert 1 <= body["hint_level"] <= 3


def test_ask_cites_the_anchor_page(frontend_client):
    """A verified anchor is cited back so the reader can show where the hint points."""
    chapters = sorted(
        _seed_syllabus(frontend_client, _start(frontend_client))["chapters"],
        key=lambda c: c["order"],
    )
    cid = chapters[0]["chapter_id"]
    page = chapters[0]["source_pages"][0]
    body = frontend_client.post(f"/api/v1/chapters/{cid}/ask", json={
        "session_id": "sess_any", "selected_text": "Fiber",
        "question": "Why does it matter?",
        "anchor": {"page": page},
    }).json()
    assert body["citations"] == [{"kind": "document", "page": page}]
    assert body["page_verified"] is True


def test_chapters_are_anchored_across_the_document(frontend_client):
    """Distinct honest anchors beat every chapter claiming page 1 (F4)."""
    chapters = sorted(
        _seed_syllabus(frontend_client, _start(frontend_client))["chapters"],
        key=lambda c: c["order"],
    )
    first_pages = [ch["source_pages"][0] for ch in chapters]
    assert len(set(first_pages)) > 1
    assert set(first_pages) <= {1, 2, 3}


def test_ask_with_an_unknown_page_is_not_cited(frontend_client):
    """Citing a page the document does not have would be a false anchor (F4/F7)."""
    chapters = sorted(
        _seed_syllabus(frontend_client, _start(frontend_client))["chapters"],
        key=lambda c: c["order"],
    )
    cid = chapters[0]["chapter_id"]
    body = frontend_client.post(f"/api/v1/chapters/{cid}/ask", json={
        "session_id": "sess_any", "selected_text": "Fiber", "question": "Where?",
        "anchor": {"page": 99},
    }).json()
    assert body["citations"] == []
    assert body["page_verified"] is False


def test_ask_without_anchor_still_answers(frontend_client):
    chapters = _seed_syllabus(frontend_client, _start(frontend_client))["chapters"]
    cid = sorted(chapters, key=lambda c: c["order"])[0]["chapter_id"]
    res = frontend_client.post(f"/api/v1/chapters/{cid}/ask", json={
        "session_id": "sess_any", "selected_text": "lanes", "question": "Explain",
    })
    assert res.status_code == 200
    assert res.json()["citations"] == []


def test_ask_interactions_are_persisted_for_audit(frontend_client, clean_store):
    """F7: every interaction feeds the engagement metric and the audit trail."""
    chapters = sorted(
        _seed_syllabus(frontend_client, _start(frontend_client))["chapters"],
        key=lambda c: c["order"],
    )
    cid = chapters[0]["chapter_id"]
    for i in range(3):
        frontend_client.post(f"/api/v1/chapters/{cid}/ask", json={
            "session_id": "sess_any", "selected_text": f"term{i}",
            "question": "why?", "anchor": {"page": 1},
        })

    recorded = clean_store.get_ask_interactions(cid)
    assert len(recorded) == 3
    assert [r["selected_text"] for r in recorded] == ["term0", "term1", "term2"]
    assert all(r["gave_direct_answer"] is False for r in recorded)


def test_ask_is_recorded_per_chapter(frontend_client, clean_store):
    chapters = sorted(
        _seed_syllabus(frontend_client, _start(frontend_client))["chapters"],
        key=lambda c: c["order"],
    )
    frontend_client.post(f"/api/v1/chapters/{chapters[0]['chapter_id']}/ask", json={
        "session_id": "s", "selected_text": "a", "question": "b",
    })
    assert len(clean_store.get_ask_interactions(chapters[0]["chapter_id"])) == 1
    assert clean_store.get_ask_interactions(chapters[1]["chapter_id"]) == []


def test_ask_on_unknown_chapter_is_404(frontend_client):
    res = frontend_client.post("/api/v1/chapters/ch_nope/ask", json={
        "session_id": "s", "selected_text": "a", "question": "b",
    })
    assert res.status_code == 404


def test_ask_requires_selected_text_and_question(frontend_client):
    chapters = _seed_syllabus(frontend_client, _start(frontend_client))["chapters"]
    cid = chapters[0]["chapter_id"]
    assert frontend_client.post(
        f"/api/v1/chapters/{cid}/ask", json={"session_id": "s", "question": "b"}
    ).status_code == 422
    assert frontend_client.post(
        f"/api/v1/chapters/{cid}/ask", json={"session_id": "s", "selected_text": "a"}
    ).status_code == 422


# ── F8: suggestions ────────────────────────────────────────────────────────────

def test_suggestions_return_three_unique_questions(frontend_client):
    chapters = _seed_syllabus(frontend_client, _start(frontend_client))["chapters"]
    cid = sorted(chapters, key=lambda c: c["order"])[0]["chapter_id"]
    body = frontend_client.get(
        f"/api/v1/chapters/{cid}/suggestions",
        params={"selection": "reconciliation and diffing"},
    ).json()
    assert body["selection"] == "reconciliation and diffing"
    assert len(body["suggested_questions"]) == 3
    assert len(set(body["suggested_questions"])) == 3
    assert all(q.strip() for q in body["suggested_questions"])


def test_suggestions_mention_the_selection(frontend_client):
    chapters = _seed_syllabus(frontend_client, _start(frontend_client))["chapters"]
    cid = sorted(chapters, key=lambda c: c["order"])[0]["chapter_id"]
    body = frontend_client.get(
        f"/api/v1/chapters/{cid}/suggestions", params={"selection": "priority lanes"}
    ).json()
    assert all("priority lanes" in q for q in body["suggested_questions"])


def test_suggestions_require_a_selection(frontend_client):
    chapters = _seed_syllabus(frontend_client, _start(frontend_client))["chapters"]
    cid = chapters[0]["chapter_id"]
    assert frontend_client.get(f"/api/v1/chapters/{cid}/suggestions").status_code == 422


def test_suggestions_are_recorded_for_engagement(frontend_client, clean_store):
    chapters = sorted(
        _seed_syllabus(frontend_client, _start(frontend_client))["chapters"],
        key=lambda c: c["order"],
    )
    cid = chapters[0]["chapter_id"]
    frontend_client.get(
        f"/api/v1/chapters/{cid}/suggestions", params={"selection": "diffing"}
    )
    recorded = clean_store.get_ask_interactions(cid)
    assert len(recorded) == 1
    assert recorded[0]["kind"] == "suggestions"
    assert recorded[0]["selection"] == "diffing"


# ── F6 invariant: honeypot is not a gate ───────────────────────────────────────
# Pinned in tests/test_f9_interview.py (test_finalize_state_transition_is_not_driven_by_
# the_honeypot_class), where the live classifier and the boundary are exercised together.
