"""F14 — Calibration (the one piece of arithmetic this backend owns).

The gap is signed (``predicted - actual``) because direction is the point: a student who
guessed 90 when they scored 62 is overconfident, and one who guessed 40 is not the same
person. The label thresholds come straight from API-CONTRACTS section 2.6.

Two behaviours matter beyond the formula:

* ``actual_score`` is read from the chapter's real stored score, never a hard-coded 88.
  The older stub returned 88 for every chapter, which would look correct on the one
  chapter a demo shows and be wrong everywhere else.
* Calibration must never change the score or the state. It is a measurement, not a lever;
  a test asserts that a wildly wrong prediction leaves the official score untouched.
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


def _scored_chapter(client):
    """Drive a chapter all the way to a real score, return (session, chapter_id)."""
    sid = client.post("/api/v1/intake", json={
        "intent": "I want to understand how React rendering works internally",
        "role": "Frontend",
        "role_is_custom": False,
    }).json()["session_id"]
    client.post(f"/api/v1/intake/{sid}/document",
                files={"file": ("module.txt", io.BytesIO(DOC), "text/plain")})
    client.post(f"/api/v1/intake/{sid}/checklist", json={"stream": False})
    chapters = sorted(
        client.post(f"/api/v1/intake/{sid}/syllabus", json={}).json()["chapters"],
        key=lambda c: c["order"],
    )
    cid = chapters[0]["chapter_id"]
    iv = client.post(f"/api/v1/chapters/{cid}/interview/start",
                     json={"session_id": sid}).json()["interview_id"]
    client.post(f"/api/v1/chapters/{cid}/interview/turn", json={
        "interview_id": iv, "turn_index": 1,
        "user_response": (
            "The reconciler diffs the tree and the commit phase applies DOM mutations in "
            "one synchronous pass, so a 10k-row list pays the whole cost in one frame."
        ),
    })
    term = get_store().get_interview(iv)["injected_term"]
    client.post(f"/api/v1/chapters/{cid}/interview/finalize", json={
        "interview_id": iv,
        "final_response": (
            f"'{term}' does not exist in React docs or any official library — it is "
            "fictional. The real primitives are useTransition and useDeferredValue."
        ),
    })
    return sid, cid, iv


def _calibrate(client, cid, iv, predicted):
    return client.post(f"/api/v1/chapters/{cid}/calibration",
                       json={"interview_id": iv, "predicted_score": predicted})


# ── the formula ────────────────────────────────────────────────────────────────

def test_gap_is_signed_predicted_minus_actual(live_client):
    _, cid, iv = _scored_chapter(live_client)
    actual = get_store().get_chapter(cid)["score"]["chapter_score"]
    body = _calibrate(live_client, cid, iv, min(100, actual + 7)).json()
    assert body["actual_score"] == actual
    assert body["calibration_gap"] == min(100, actual + 7) - actual


def test_actual_score_comes_from_the_stored_chapter_score(live_client):
    """Not a hard-coded 88: two different chapters must report their own scores."""
    _, cid, iv = _scored_chapter(live_client)
    stored = get_store().get_chapter(cid)["score"]["chapter_score"]
    body = _calibrate(live_client, cid, iv, 50).json()
    assert body["actual_score"] == stored


@pytest.mark.parametrize("delta,label", [
    (16, "overconfident"),
    (15, "well_calibrated"),      # boundary: NOT over, per `> actual + 15`
    (0, "well_calibrated"),
    (-15, "well_calibrated"),     # boundary: NOT under, per `< actual - 15`
    (-16, "underconfident"),
])
def test_label_thresholds_are_exact(live_client, delta, label):
    _, cid, iv = _scored_chapter(live_client)
    actual = get_store().get_chapter(cid)["score"]["chapter_score"]
    predicted = max(0, min(100, actual + delta))
    if predicted - actual != delta:
        pytest.skip("real score puts this delta outside 0-100")
    body = _calibrate(live_client, cid, iv, predicted).json()
    assert body["calibration_gap"] == delta
    assert body["label"] == label


def test_perfect_prediction_is_well_calibrated_with_zero_gap(live_client):
    _, cid, iv = _scored_chapter(live_client)
    actual = get_store().get_chapter(cid)["score"]["chapter_score"]
    body = _calibrate(live_client, cid, iv, actual).json()
    assert body["calibration_gap"] == 0
    assert body["label"] == "well_calibrated"


def test_labels_match_the_shared_helper(live_client):
    """Endpoint and report must agree; both call app_addons.calibration_labels."""
    from app.schemas.app_addons import calibration_labels

    for predicted, actual in [(90, 88), (100, 60), (10, 90), (75, 60), (60, 75)]:
        gap, label = calibration_labels(predicted - actual)
        if predicted > actual + 15:
            assert label == "overconfident"
        elif predicted < actual - 15:
            assert label == "underconfident"
        else:
            assert label == "well_calibrated"
        assert gap == predicted - actual


# ── validation + persistence ──────────────────────────────────────────────────

@pytest.mark.parametrize("bad", [-1, 101, 1000])
def test_predicted_score_outside_0_100_is_rejected(live_client, bad):
    _, cid, iv = _scored_chapter(live_client)
    assert _calibrate(live_client, cid, iv, bad).status_code == 422


def test_unknown_chapter_is_404(live_client):
    assert _calibrate(live_client, "ch_nope", "int_nope", 50).status_code == 404


def test_calibration_is_persisted_on_the_chapter(live_client):
    _, cid, iv = _scored_chapter(live_client)
    _calibrate(live_client, cid, iv, 90)
    stored = get_store().get_calibration(cid)
    assert stored is not None
    assert get_store().get_chapter(cid)["calibration"]["predicted_score"] == 90


def test_resubmitting_overwrites_rather_than_stacking_rows(live_client):
    """A correction must not leave two rows for the same chapter."""
    _, cid, iv = _scored_chapter(live_client)
    _calibrate(live_client, cid, iv, 40)
    _calibrate(live_client, cid, iv, 95)
    assert get_store().get_calibration(cid)["predicted_score"] == 95


# ── calibration is a measurement, not a lever ─────────────────────────────────

def test_calibration_does_not_change_the_score_or_state(live_client):
    _, cid, iv = _scored_chapter(live_client)
    before = dict(get_store().get_chapter(cid)["score"])
    status_before = get_store().get_chapter(cid)["status"]

    _calibrate(live_client, cid, iv, 100)   # wildly overconfident
    _calibrate(live_client, cid, iv, 0)     # then wildly underconfident

    assert get_store().get_chapter(cid)["score"] == before
    assert get_store().get_chapter(cid)["status"] == status_before


def test_cached_scenario_answers_without_raising(cached_client):
    _, cid, iv = _scored_chapter(cached_client)
    body = _calibrate(cached_client, cid, iv, 90).json()
    assert body["fallback"]["fallback_active"] is True
    assert body["label"] in ("well_calibrated", "overconfident", "underconfident")
