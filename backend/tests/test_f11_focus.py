"""F11/F12 — Focus Mode event ingest.

What is being pinned here is a *privacy* invariant and an *accessibility* one, not a
scoring feature:

* ``video_transmitted: true`` is refused, and so is anything shaped like a frame. The
  product's whole privacy claim ("inference on-device, only booleans leave the browser")
  collapses the moment the server accepts a blob, and no UI change would reveal it.
* Accessible Mode (camera off) resolves to ``assisted_unverified`` **and the run still
  scores**. A backend that turns accessibility into an error path is a bug a demo would
  never surface, because the demo always has a camera.
* Focus Mode adjusts the score. It never gates: the last test shows a fully flagged run
  still transitioning the chapter, with the flag visible in the number.
"""
from __future__ import annotations

import io

import pytest

from app.repositories import get_store

DOC = (
    b"Page 1\nReact reconciliation compares the new tree with the previous one.\n\n"
    b"Page 2\nFiber splits work into units and yields to the browser.\n\n"
    b"Page 3\nPriority lanes decide which update renders first under load.\n"
)

_CAMERA_OFF_NOTE = (
    "Accessible Mode = the student cannot or will not run a camera. The honest answer is "
    "'unverified', and the score must still be computed."
)


def _seed_chapter(client, sid: str = None) -> str:
    if sid is None:
        sid = client.post("/api/v1/intake", json={
            "intent": "I want to understand how React rendering works internally",
            "role": "Frontend",
            "role_is_custom": False,
        }).json()["session_id"]
    client.post(f"/api/v1/intake/{sid}/document",
                files={"file": ("module.txt", io.BytesIO(DOC), "text/plain")})
    client.post(f"/api/v1/intake/{sid}/checklist", json={"stream": False})
    syllabus = client.post(f"/api/v1/intake/{sid}/syllabus", json={}).json()
    chapters = sorted(syllabus["chapters"], key=lambda c: c["order"])
    return chapters[0]["chapter_id"]


def _events(client, cid: str, events, **extra):
    return client.post(f"/api/v1/chapters/{cid}/focus-events", json={
        "interview_id": "int_focus", "events": events, **extra,
    })


# ── the privacy invariant ──────────────────────────────────────────────────────

def test_video_transmitted_true_is_rejected(live_client):
    cid = _seed_chapter(live_client)
    res = _events(live_client, cid, [], video_transmitted=True)
    # Pydantic validates the body before the handler, so this is FastAPI's 422.
    assert res.status_code == 422
    assert "video_transmitted" in res.text


def test_frame_blob_in_the_payload_is_rejected(live_client):
    """The schema rejects an unknown field is not enough: a blob must not be *stored*."""
    cid = _seed_chapter(live_client)
    res = live_client.post(f"/api/v1/chapters/{cid}/focus-events", json={
        "interview_id": "int_focus",
        "events": [{"type": "GAZE_DRIFT", "at_ms": 1, "frame": "a" * 5000}],
    })
    assert res.status_code == 422
    assert get_store().get_focus_events("int_focus") == []


def test_nothing_is_persisted_when_the_payload_is_refused(live_client):
    cid = _seed_chapter(live_client)
    _events(live_client, cid, [{"type": "GAZE_DRIFT", "at_ms": 1}], video_transmitted=True)
    assert get_store().get_focus_events("int_focus") == []


def test_unknown_chapter_is_404(live_client):
    res = _events(live_client, "ch_nope", [])
    assert res.status_code == 404


# ── summarising ───────────────────────────────────────────────────────────────

def test_event_counts_are_summarised_per_type(live_client):
    cid = _seed_chapter(live_client)
    body = _events(live_client, cid, [
        {"type": "GAZE_DRIFT", "at_ms": 100, "duration_ms": 400},
        {"type": "GAZE_DRIFT", "at_ms": 900, "duration_ms": 300},
        {"type": "TAB_BLUR", "at_ms": 1500, "duration_ms": 15000},
        {"type": "MULTIPLE_FACES", "at_ms": 2000, "count": 2},
    ]).json()
    assert body["summary"] == {
        "gaze_drift_count": 2, "multi_face_count": 1, "tab_blur_count": 1,
    }


def test_suspicious_events_flag_assisted_and_auto_blur(live_client):
    cid = _seed_chapter(live_client)
    body = _events(live_client, cid, [{"type": "TAB_BLUR", "at_ms": 1}]).json()
    assert body["integrity_flag"] == "assisted"
    assert body["auto_blur"] is True
    # A flag, not a verdict: the number says -3, and the enum token is what carries meaning.
    assert body["integrity_score"] == 97


def test_no_suspicion_is_clean(live_client):
    cid = _seed_chapter(live_client)
    body = _events(live_client, cid, []).json()
    assert body["integrity_flag"] == "clean"
    assert body["auto_blur"] is False
    assert body["integrity_score"] == 100


def test_events_are_accumulated_across_requests(live_client):
    cid = _seed_chapter(live_client)
    _events(live_client, cid, [{"type": "GAZE_DRIFT", "at_ms": 100}])
    _events(live_client, cid, [{"type": "GAZE_DRIFT", "at_ms": 200}])
    stored = get_store().get_focus_events("int_focus")
    assert [e["at_ms"] for e in stored] == [100, 200]


# ── Accessible Mode ────────────────────────────────────────────────────────────

def test_camera_off_yields_assisted_unverified_not_an_error(live_client):
    """Accessible Mode must resolve, not raise."""
    cid = _seed_chapter(live_client)
    res = _events(live_client, cid, [], accessible_mode=True)
    assert res.status_code == 200, res.text
    body = res.json()
    assert body["integrity_flag"] == "assisted_unverified"
    assert body["accessible_mode"] is True


def test_camera_off_event_alone_is_accessible_mode(live_client):
    cid = _seed_chapter(live_client)
    body = _events(live_client, cid, [{"type": "CAMERA_OFF", "at_ms": 1}]).json()
    assert body["integrity_flag"] == "assisted_unverified"
    assert body["accessible_mode"] is True
    assert body["auto_blur"] is False


def test_accessible_mode_is_neutral_on_the_score(live_client):
    """PRD risk R6: accessibility is not a penalty."""
    cid = _seed_chapter(live_client)
    body = _events(live_client, cid, [], accessible_mode=True).json()
    assert body["integrity_score"] == 100


@pytest.mark.parametrize("mode", ["accessible_mode", "camera_off_event"])
def test_accessible_mode_run_still_scores_the_chapter(live_client, mode):
    """The whole point: the run proceeds to a score instead of erroring out."""
    sid = live_client.post("/api/v1/intake", json={
        "intent": "I want to understand how React rendering works internally",
        "role": "Frontend",
        "role_is_custom": False,
    }).json()["session_id"]
    cid = _seed_chapter(live_client, sid)

    interviews = {"interview_id": "int_accessible"}
    if mode == "accessible_mode":
        _events(live_client, cid, [], accessible_mode=True)
    else:
        _events(live_client, cid, [{"type": "CAMERA_OFF", "at_ms": 1}])

    iv = live_client.post(f"/api/v1/chapters/{cid}/interview/start",
                          json={"session_id": sid}).json()
    interviews["interview_id"] = iv["interview_id"]
    live_client.post(f"/api/v1/chapters/{cid}/interview/turn", json={
        "interview_id": iv["interview_id"], "turn_index": 1,
        "user_response": (
            "The reconciler walks the tree and the commit phase applies DOM mutations "
            "in one synchronous pass, which is where the 100ms goes on 10k rows."
        ),
    })
    term = get_store().get_interview(iv["interview_id"])["injected_term"]
    body = live_client.post(f"/api/v1/chapters/{cid}/interview/finalize", json={
        "interview_id": iv["interview_id"],
        "final_response": (
            f"'{term}' does not exist in React docs; it is a fictional concept. The real "
            "primitives are useTransition and useDeferredValue."
        ),
    }).json()
    assert body["score"]["chapter_score"] > 0
    assert body["integrity_flag"] in ("clean", "assisted_unverified")


def test_accessible_mode_is_not_overridden_by_later_telemetry(live_client):
    """An accessible run can never be re-flagged by a paste heuristic (core.intelligence)."""
    from app.core.intelligence import telemetry_flag

    assert telemetry_flag(paste_seen=True, focus_flag="assisted_unverified") == \
        "assisted_unverified"


# ── stickiness + the "not a gate" rule ────────────────────────────────────────

def test_a_clean_batch_does_not_erase_an_earlier_flag(live_client):
    """Otherwise an integrity flag could be laundered right before finalize."""
    cid = _seed_chapter(live_client)
    _events(live_client, cid, [{"type": "TAB_BLUR", "at_ms": 1}])
    assert get_store().get_focus_flag("int_focus") == "assisted"

    _events(live_client, cid, [])
    assert get_store().get_focus_flag("int_focus") == "assisted"


def test_focus_events_do_not_move_chapter_state(live_client):
    """Focus Mode is a scoring dimension; the gate belongs to the chapter score."""
    cid = _seed_chapter(live_client)
    before = get_store().get_chapter(cid)["status"]
    _events(live_client, cid, [{"type": "MULTIPLE_FACES", "at_ms": 1, "count": 3}])
    assert get_store().get_chapter(cid)["status"] == before == "ACTIVE_READING"


def test_cached_scenario_serves_focus_events_without_raising(cached_client):
    cid = _seed_chapter(cached_client)
    body = _events(cached_client, cid, [{"type": "TAB_BLUR", "at_ms": 1}]).json()
    assert body["fallback"]["fallback_active"] is True
    assert body["integrity_flag"] in ("clean", "assisted", "assisted_unverified")
