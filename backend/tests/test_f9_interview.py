"""F9/F10/F13 — Interview quiz (multi-turn + honeypot) and score persistence.

Contract under test: ``POST /api/v1/chapters/:id/interview/{start,turn,finalize}``.

Rules that must hold:
* ``start`` creates an interview, sets ``turn_index = 1`` and moves the chapter to
  ``INTERVIEW`` (state is the backend's, F9).
* ``turn`` persists the turn history **and** the client telemetry
  (``paste_detected`` / ``duration_seconds`` / ``keystroke_cpm``) — that telemetry feeds
  the deterministic pre-filter in ADR 002 s2.1, so it must not be dropped even when it
  looks unused.
* ``finalize`` calls scoring, writes ``chapter_score``, transitions the state, and
  computes ``next_unlocked_chapter_id``. Threshold: ``>= 75`` -> UNLOCKED,
  ``< 75`` -> NEEDS_REVIEW (a retry, never a dead end).
* Honeypot metadata validation is NOT the backend's job: store it as received.
"""
from __future__ import annotations

import io
from typing import Any, Dict

import pytest

from app.core.state_machine import apply_score
from app.repositories import get_store


@pytest.fixture()
def frontend_client(live_client):
    """Override conftest: this module tests the LIVE path, not the frozen scenario.

    With DEMO_MODE=cached, every endpoint short-circuits to the pre-baked scenario, so
    a classifier or threshold assertion would be checking the fixture rather than the
    logic. The two cached-scenario tests below ask for ``cached_client`` explicitly.
    """
    return live_client


def _seed(frontend_client):
    sid = frontend_client.post("/api/v1/intake", json={
        "intent": "I want to understand how React rendering works internally",
        "role": "Frontend",
    }).json()["session_id"]
    frontend_client.post(
        f"/api/v1/intake/{sid}/document",
        files={"file": ("m.txt", io.BytesIO(
            b"Page 1\nReact reconciliation compares trees.\n\n"
            b"Page 2\nFiber splits work into units.\n\n"
            b"Page 3\nPriority lanes order work."
        ), "text/plain")},
    )
    frontend_client.post(f"/api/v1/intake/{sid}/checklist", json={})
    chapters = frontend_client.post(f"/api/v1/intake/{sid}/syllabus", json={}).json()["chapters"]
    chapters = sorted(chapters, key=lambda c: c["order"])
    return sid, chapters


def _start_interview(frontend_client, cid: str, sid: str = "sess_x"):
    res = frontend_client.post(f"/api/v1/chapters/{cid}/interview/start", json={
        "session_id": sid,
    })
    assert res.status_code == 200, res.text
    return res.json()


def _drive_to_honeypot(frontend_client, cid: str, interview_id: str) -> Dict[str, Any]:
    """Send turn 1 and return the turn-2 response that carries the injected term.

    The catalog rotates terms per chapter and picks variants deterministically, so tests
    read the injected term instead of hard-coding one — a hard-coded term would also
    silently stop testing the classifier the day the catalog changes.
    """
    return frontend_client.post(f"/api/v1/chapters/{cid}/interview/turn", json={
        "interview_id": interview_id,
        "turn_index": 1,
        "user_response": (
            "VDOM diffing costs CPU on 10k items because the reconciler walks the whole "
            "tree, and the commit phase then applies the DOM mutations in one pass."
        ),
        "client_telemetry": {"paste_detected": False, "duration_seconds": 38,
                             "keystroke_cpm": 260},
    }).json()


# ── start ──────────────────────────────────────────────────────────────────────

def test_start_creates_interview_and_moves_chapter_to_interview(frontend_client):
    sid, chapters = _seed(frontend_client)
    cid = chapters[0]["chapter_id"]
    body = _start_interview(frontend_client, cid, sid)

    assert body["interview_id"].startswith("int_")
    assert body["chapter_id"] == cid
    assert body["turn_index"] == 1
    assert body["first_question"].strip()
    assert body["focus_mode"] == {"required": False, "available": True}
    assert get_store().get_chapter(cid)["status"] == "INTERVIEW"


def test_first_question_is_inferential_not_a_definition(frontend_client):
    """PRD section 4.5: HOTS questions, not 'what is X'."""
    sid, chapters = _seed(frontend_client)
    body = _start_interview(frontend_client, chapters[0]["chapter_id"], sid)
    lowered = body["first_question"].lower()
    assert "what is" not in lowered
    assert len(body["first_question"].split()) >= 8


def test_start_on_a_locked_chapter_is_refused(frontend_client):
    """The gate must hold at the API, not only in the UI."""
    sid, chapters = _seed(frontend_client)
    res = frontend_client.post(
        f"/api/v1/chapters/{chapters[1]['chapter_id']}/interview/start",
        json={"session_id": sid},
    )
    assert res.status_code == 409


def test_start_on_unknown_chapter_is_404(frontend_client):
    res = frontend_client.post(
        "/api/v1/chapters/ch_nope/interview/start", json={"session_id": "s"}
    )
    assert res.status_code == 404


def test_start_persists_the_interview(frontend_client):
    sid, chapters = _seed(frontend_client)
    body = _start_interview(frontend_client, chapters[0]["chapter_id"], sid)
    stored = get_store().get_interview(body["interview_id"])
    assert stored is not None
    assert stored["chapter_id"] == chapters[0]["chapter_id"]
    assert stored["session_id"] == sid


# ── turn ───────────────────────────────────────────────────────────────────────

def test_turn_advances_and_injects_the_honeypot_on_turn_two(frontend_client):
    sid, chapters = _seed(frontend_client)
    cid = chapters[0]["chapter_id"]
    iv = _start_interview(frontend_client, cid, sid)
    body = _drive_to_honeypot(frontend_client, cid, iv["interview_id"])

    assert body["turn_index"] == 2
    assert body["honeypot_active"] is True
    term = body["honeypot_metadata"]["injected_term"]
    # The term must come from the deterministic catalog, not be invented per call.
    from ai import catalog as honeypot_catalog

    catalog_terms = {e["term"] for e in honeypot_catalog.load_catalog()}
    variants = {v for e in honeypot_catalog.load_catalog() for v in e.get("variants", [])}
    assert term in catalog_terms | variants
    assert body["honeypot_metadata"]["expected_action"] == "REJECT_AS_FICTITIOUS"
    assert body["honeypot_metadata"]["source"] == "deterministic_catalog"
    assert body["running_score"] > 0
    assert body["is_concluded"] is False


def test_turn_persists_history_and_telemetry(frontend_client):
    """Telemetry must survive: ADR 002 s2.1 pre-filter reads it (DEV 2 F9 note)."""
    sid, chapters = _seed(frontend_client)
    cid = chapters[0]["chapter_id"]
    iv = _start_interview(frontend_client, cid, sid)

    frontend_client.post(f"/api/v1/chapters/{cid}/interview/turn", json={
        "interview_id": iv["interview_id"], "turn_index": 1,
        "user_response": "Long reasoned answer about reconciliation cost " * 3,
        "client_telemetry": {"paste_detected": True, "duration_seconds": 2,
                             "keystroke_cpm": 900},
    })
    stored = get_store().get_interview(iv["interview_id"])
    assert len(stored["turns"]) == 1
    turn = stored["turns"][0]
    assert turn["role"] == "user"
    assert turn["client_telemetry"]["paste_detected"] is True
    assert turn["client_telemetry"]["keystroke_cpm"] == 900
    assert turn["client_telemetry"]["duration_seconds"] == 2


def test_turn_on_unknown_interview_is_404(frontend_client):
    sid, chapters = _seed(frontend_client)
    res = frontend_client.post(
        f"/api/v1/chapters/{chapters[0]['chapter_id']}/interview/turn",
        json={"interview_id": "int_nope", "turn_index": 1, "user_response": "x"},
    )
    assert res.status_code == 404


def test_second_turn_does_not_reinject_a_honeypot(frontend_client):
    """One injection per interview: a second fake term would look like a bug."""
    sid, chapters = _seed(frontend_client)
    cid = chapters[0]["chapter_id"]
    iv = _start_interview(frontend_client, cid, sid)
    payload = {"interview_id": iv["interview_id"], "user_response": "a long enough answer " * 3}

    first = frontend_client.post(
        f"/api/v1/chapters/{cid}/interview/turn", json={**payload, "turn_index": 1}
    ).json()
    second = frontend_client.post(
        f"/api/v1/chapters/{cid}/interview/turn", json={**payload, "turn_index": 2}
    ).json()
    assert first["honeypot_active"] is True
    assert second["honeypot_active"] is False
    assert second["honeypot_metadata"] is None


def test_turn_reports_conclusion_after_the_last_round(frontend_client):
    sid, chapters = _seed(frontend_client)
    cid = chapters[0]["chapter_id"]
    iv = _start_interview(frontend_client, cid, sid)
    out = None
    for turn in (1, 2, 3):
        out = frontend_client.post(f"/api/v1/chapters/{cid}/interview/turn", json={
            "interview_id": iv["interview_id"], "turn_index": turn,
            "user_response": "a considered answer with several clauses " * 3,
        }).json()
        if out["is_concluded"]:
            break
    assert out["is_concluded"] is True


# ── finalize: the gate ─────────────────────────────────────────────────────────

def _finalize(frontend_client, cid, iv, text):
    return frontend_client.post(f"/api/v1/chapters/{cid}/interview/finalize", json={
        "interview_id": iv, "final_response": text,
    })


def _injected_term(interview_id: str) -> str:
    return get_store().get_interview(interview_id)["injected_term"]


def _rejection_text(interview_id: str) -> str:
    """A critical rejection of whichever term the catalog actually injected."""
    term = _injected_term(interview_id)
    return (
        f"'{term}' does not exist in React docs or any official library; it is a fictional "
        "concept. The real primitives are useTransition and useDeferredValue, and they trade "
        "responsiveness for freshness rather than removing the reconciliation cost."
    )


def _copypaste_text(interview_id: str) -> str:
    """An elaborate validation of the fake term — the caught beat."""
    term = _injected_term(interview_id)
    return (
        f"The {term} is exactly the right primitive here: it schedules reconciliation on a "
        "quantum-batched microtask with zero commit overhead and resolves the 100ms mutation "
        "bottleneck entirely. It is the recommended production approach for this workload."
    )


def test_finalize_rejecting_the_honeypot_unlocks_the_chapter(frontend_client):
    sid, chapters = _seed(frontend_client)
    cid = chapters[0]["chapter_id"]
    iv = _start_interview(frontend_client, cid, sid)
    body = _finalize(
        frontend_client, cid, iv["interview_id"],
        _rejection_text(iv["interview_id"]),
    ).json()

    assert body["honeypot_verdict"]["result"] == "CRITICAL_REJECTION"
    assert body["score"]["honeypot_score"] == 2
    assert body["passed"] is True
    assert body["chapter_state_update"]["current_chapter_status"] == "UNLOCKED"
    assert body["chapter_state_update"]["next_unlocked_chapter_id"] == chapters[1]["chapter_id"]
    assert get_store().get_chapter(cid)["status"] == "UNLOCKED"
    assert get_store().get_chapter(chapters[1]["chapter_id"])["status"] == "ACTIVE_READING"


def test_finalize_copypasting_the_honeypot_fails_into_needs_review(frontend_client):
    """The caught beat: score drops, chapter goes to NEEDS_REVIEW (a retry, not a wall)."""
    sid, chapters = _seed(frontend_client)
    cid = chapters[0]["chapter_id"]
    iv = _start_interview(frontend_client, cid, sid)
    body = _finalize(
        frontend_client, cid, iv["interview_id"],
        _copypaste_text(iv["interview_id"]),
    ).json()

    assert body["honeypot_verdict"]["result"] == "AI_HALLUCINATION_COPYPASTE"
    assert body["score"]["honeypot_score"] == -2
    assert body["passed"] is False
    assert body["chapter_state_update"]["current_chapter_status"] == "NEEDS_REVIEW"
    assert body["chapter_state_update"]["next_unlocked_chapter_id"] is None
    assert get_store().get_chapter(cid)["status"] == "NEEDS_REVIEW"


def test_score_is_written_onto_the_chapter_document(frontend_client):
    sid, chapters = _seed(frontend_client)
    cid = chapters[0]["chapter_id"]
    iv = _start_interview(frontend_client, cid, sid)
    _finalize(frontend_client, cid, iv["interview_id"],
              _rejection_text(iv["interview_id"]))

    chapter = get_store().get_chapter(cid)
    assert chapter["score"]["chapter_score"] >= 75
    assert set(chapter["score"]) >= {
        "chapter_score", "reasoning_score", "integrity_score", "honeypot_score"
    }


def test_single_score_only_not_dual_metric(frontend_client):
    """PRD section 8: dual-metric was cut; one score per chapter."""
    sid, chapters = _seed(frontend_client)
    cid = chapters[0]["chapter_id"]
    iv = _start_interview(frontend_client, cid, sid)
    body = _finalize(frontend_client, cid, iv["interview_id"],
                     _rejection_text(iv["interview_id"])).json()
    score = body["score"]
    assert isinstance(score["chapter_score"], int)
    assert not any("concept_score" in k for k in score)


def test_threshold_boundary_75_unlocks_and_74_does_not(frontend_client):
    """Pin the exact boundary: the gate is on chapter_score >= 75."""
    sid, chapters = _seed(frontend_client)
    cid = chapters[0]["chapter_id"]
    store = get_store()

    store.set_chapter_status(cid, "INTERVIEW")
    above = apply_score(cid, {"chapter_score": 75, "reasoning_score": 75,
                                       "integrity_score": 100, "honeypot_score": 0})
    assert above["passed"] is True

    store.set_chapter_status(cid, "INTERVIEW")
    below = apply_score(cid, {"chapter_score": 74, "reasoning_score": 74,
                                       "integrity_score": 100, "honeypot_score": 0})
    assert below["passed"] is False
    assert below["status"] == "NEEDS_REVIEW"


def test_needs_review_chapter_can_retry_the_interview(frontend_client):
    """NEEDS_REVIEW is a retry path, not a dead end (F9)."""
    sid, chapters = _seed(frontend_client)
    cid = chapters[0]["chapter_id"]
    iv = _start_interview(frontend_client, cid, sid)
    _finalize(frontend_client, cid, iv["interview_id"], _copypaste_text(iv["interview_id"]))
    assert get_store().get_chapter(cid)["status"] == "NEEDS_REVIEW"

    res = frontend_client.post(f"/api/v1/chapters/{cid}/interview/start",
                               json={"session_id": sid})
    assert res.status_code == 200
    assert get_store().get_chapter(cid)["status"] == "INTERVIEW"


def test_finalize_carries_verifier_second_opinion(frontend_client):
    sid, chapters = _seed(frontend_client)
    cid = chapters[0]["chapter_id"]
    iv = _start_interview(frontend_client, cid, sid)
    body = _finalize(frontend_client, cid, iv["interview_id"],
                     _rejection_text(iv["interview_id"])).json()
    assert body["verifier"]["status"] in ("agreed", "uncertain")
    assert body["verifier"]["note"].strip()


def test_finalize_marks_a_verifier_doubted_score_not_passing(frontend_client, clean_store):
    """The verifier loop must be binding (risk R3), not decoration."""
    from app.core.scoring import apply_verifier

    capped = apply_verifier(
        {"chapter_score": 92, "reasoning_score": 90, "integrity_score": 100,
         "honeypot_score": 2},
        {"status": "uncertain", "note": "score looks generous"},
    )
    assert capped["chapter_score"] < 75
    # The raw reasoning measurement is preserved so the report can show both.
    assert capped["reasoning_score"] == 90


def test_finalize_records_the_honeypot_verdict_on_the_chapter(frontend_client):
    sid, chapters = _seed(frontend_client)
    cid = chapters[0]["chapter_id"]
    iv = _start_interview(frontend_client, cid, sid)
    _finalize(frontend_client, cid, iv["interview_id"],
              "React Quantum Hook does not exist; fictional term.")
    chapter = get_store().get_chapter(cid)
    assert chapter["honeypot_verdict"]["result"] == "CRITICAL_REJECTION"
    assert chapter["interview_id"] == iv["interview_id"]


def test_finalize_unknown_interview_is_404(frontend_client):
    sid, chapters = _seed(frontend_client)
    res = _finalize(frontend_client, chapters[0]["chapter_id"], "int_nope", "text")
    assert res.status_code == 404


def test_finalize_requires_a_response(frontend_client):
    sid, chapters = _seed(frontend_client)
    cid = chapters[0]["chapter_id"]
    iv = _start_interview(frontend_client, cid, sid)
    res = _finalize(frontend_client, cid, iv["interview_id"], "")
    assert res.status_code == 422


def test_finalize_state_transition_is_not_driven_by_the_honeypot_class(frontend_client):
    """Rejecting the honeypot is NOT what unlocks: the threshold decides.

    A chapter with a rejected honeypot but a weak reasoning score must still fail, or
    the honeypot quietly becomes a gate (API-CONTRACTS section 1).
    """
    sid, chapters = _seed(frontend_client)
    cid = chapters[0]["chapter_id"]
    get_store().set_chapter_status(cid, "INTERVIEW")
    outcome = apply_score(cid, {
        "chapter_score": 60, "reasoning_score": 60, "integrity_score": 100,
        "honeypot_score": 2,
    })
    assert outcome["passed"] is False
    assert outcome["status"] == "NEEDS_REVIEW"


# ── F17: cached scenario finalize ──────────────────────────────────────────────

def test_cached_success_scenario_ends_in_critical_rejection(cached_client):
    sid = cached_client.post("/api/v1/intake", json={
        "intent": "I want to understand how React rendering works internally",
        "role": "Frontend",
    }).json()["session_id"]
    cached_client.post(f"/api/v1/intake/{sid}/checklist", json={})
    chapters = sorted(
        cached_client.post(f"/api/v1/intake/{sid}/syllabus", json={}).json()["chapters"],
        key=lambda c: c["order"],
    )
    cid = chapters[0]["chapter_id"]
    iv = cached_client.post(f"/api/v1/chapters/{cid}/interview/start",
                            json={"session_id": sid}).json()
    body = cached_client.post(f"/api/v1/chapters/{cid}/interview/finalize", json={
        "interview_id": iv["interview_id"],
        "final_response": "Whatever the student typed.",
    }).json()
    assert body["honeypot_verdict"]["result"] == "CRITICAL_REJECTION"
    assert body["passed"] is True
    assert body["fallback"]["fallback_active"] is True
    assert body["fallback"]["scenario"] == "success"


def test_cached_caught_scenario_ends_in_copypaste_and_fails(cached_client):
    """Both demo beats must be reachable from the cached path alone."""
    sid = cached_client.post("/api/v1/intake", json={
        "intent": "I want to understand how React rendering works internally",
        "role": "Frontend",
    }).json()["session_id"]
    cached_client.post(f"/api/v1/intake/{sid}/checklist", json={})
    chapters = sorted(
        cached_client.post(f"/api/v1/intake/{sid}/syllabus", json={}).json()["chapters"],
        key=lambda c: c["order"],
    )
    cid = chapters[0]["chapter_id"]
    iv = cached_client.post(
        f"/api/v1/chapters/{cid}/interview/start?scenario=caught",
        json={"session_id": sid}, headers={"x-demo-mode": "cached"},
    ).json()
    body = cached_client.post(
        f"/api/v1/chapters/{cid}/interview/finalize?scenario=caught",
        json={"interview_id": iv["interview_id"], "final_response": "Anything."},
    ).json()
    assert body["honeypot_verdict"]["result"] == "AI_HALLUCINATION_COPYPASTE"
    assert body["passed"] is False
    assert body["fallback"]["scenario"] == "caught"
