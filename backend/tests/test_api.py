"""Deployment smoke test: the full flow in one run, end to end.

Kept separate from the per-feature suites (``test_f*_*.py``) on purpose. Those pin
individual contracts; this one answers a different question — "does the whole journey
still work as a single sequence?" — which is what the Hari 3 gate requires (WBS section
5: online **and** cached must both run twice in a row with no blank spinner).

Replaces an older smoke test that called ``finalize`` with an interview id that never
existed (it asserted 200 against a request the API now correctly rejects with 404).
"""
from __future__ import annotations

import io

from app.repositories import get_store

DOC = (
    b"Page 1\nReact reconciliation compares the new tree with the previous one.\n\n"
    b"Page 2\nFiber splits work into units and yields to the browser.\n\n"
    b"Page 3\nPriority lanes decide which update renders first under load.\n"
)


def _run_full_flow(client) -> dict:
    """intake -> document -> checklist -> syllabus -> reader -> interview -> finalize."""
    intake = client.post("/api/v1/intake", json={
        "intent": "I want to understand how React rendering works internally",
        "role": "Frontend",
        "role_is_custom": False,
    })
    assert intake.status_code == 201, intake.text
    sid = intake.json()["session_id"]

    upload = client.post(
        f"/api/v1/intake/{sid}/document",
        files={"file": ("module.txt", io.BytesIO(DOC), "text/plain")},
    )
    assert upload.status_code == 201, upload.text
    assert upload.json()["total_pages"] == 3

    checklist = client.post(f"/api/v1/intake/{sid}/checklist", json={"stream": False})
    assert checklist.status_code == 200
    selected = [i["item_id"] for i in checklist.json()["checklist"] if i["selected"]]
    assert selected

    assert client.put(
        f"/api/v1/intake/{sid}/checklist", json={"selected_item_ids": selected}
    ).status_code == 200

    syllabus = client.post(f"/api/v1/intake/{sid}/syllabus", json={})
    assert syllabus.status_code == 201, syllabus.text
    chapters = sorted(syllabus.json()["chapters"], key=lambda c: c["order"])
    cid = chapters[0]["chapter_id"]

    reader = client.get(f"/api/v1/chapters/{cid}")
    assert reader.status_code == 200
    assert reader.json()["status"] == "ACTIVE_READING"

    interview = client.post(
        f"/api/v1/chapters/{cid}/interview/start", json={"session_id": sid}
    )
    assert interview.status_code == 200, interview.text
    interview_id = interview.json()["interview_id"]

    turn = client.post(f"/api/v1/chapters/{cid}/interview/turn", json={
        "interview_id": interview_id,
        "turn_index": 1,
        "user_response": (
            "VDOM diffing costs CPU on 10k items because the reconciler walks the tree "
            "and the commit phase applies the DOM mutations in one synchronous pass."
        ),
        "client_telemetry": {"paste_detected": False, "duration_seconds": 38,
                             "keystroke_cpm": 260},
    })
    assert turn.status_code == 200, turn.text
    assert turn.json()["honeypot_active"] is True

    term = get_store().get_interview(interview_id)["injected_term"]
    finalize = client.post(f"/api/v1/chapters/{cid}/interview/finalize", json={
        "interview_id": interview_id,
        "final_response": (
            f"'{term}' does not exist in React docs or any official library; it is a "
            "fictional concept. The real primitives are useTransition and useDeferredValue."
        ),
    })
    assert finalize.status_code == 200, finalize.text
    return {"session_id": sid, "chapter_id": cid, "finalize": finalize.json()}


def test_full_flow_live_path(live_client):
    """The whole journey on the live code path, start to finish."""
    result = _run_full_flow(live_client)
    body = result["finalize"]
    assert body["honeypot_verdict"]["result"] == "CRITICAL_REJECTION"
    assert body["chapter_state_update"]["current_chapter_status"] == "UNLOCKED"


def test_full_flow_runs_twice_in_a_row_live(live_client):
    """Hari 3 gate: two consecutive clean runs, no leftover state between them."""
    first = _run_full_flow(live_client)
    second = _run_full_flow(live_client)
    assert first["session_id"] != second["session_id"]
    assert second["finalize"]["passed"] is True


def test_full_flow_cached_path(cached_client):
    """Same journey with the demo cache: the recording path must not raise either."""
    result = _run_full_flow(cached_client)
    body = result["finalize"]
    assert body["fallback"]["fallback_active"] is True
    assert body["fallback"]["source"] == "LOCAL_DETERMINISTIC_CACHE"
    assert body["chapter_state_update"]["current_chapter_status"] == "UNLOCKED"


def test_full_flow_runs_twice_in_a_row_cached(cached_client):
    """Golden rule 1: no blank spinner, and no second-run drift either."""
    first = _run_full_flow(cached_client)
    second = _run_full_flow(cached_client)
    assert first["finalize"]["score"] == second["finalize"]["score"]
    assert first["finalize"]["honeypot_verdict"] == second["finalize"]["honeypot_verdict"]


def test_health_check(client):
    body = client.get("/health").json()
    assert body["status"] == "healthy"
    assert body["demo_mode"] in ("live", "cached")


def test_roles_endpoint(client):
    body = client.get("/api/v1/roles").json()
    assert "Frontend" in body["roles"]
    assert body["others_option"] == "Others"
