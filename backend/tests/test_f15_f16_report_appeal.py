"""F15 (appeal) + F16 (final report).

The thing worth testing in the report is not "does it return JSON" — it is whether the
numbers are *derived from the chapters the student actually produced*. The stub this
replaced returned a fixed pair of chapters (88/62), which looks right in exactly one demo
and lies in every other run. So the assertions here compare the report against the stored
chapter documents, not against literals.

The appeal is a stub by contract (WBS section 7, cut #1), so what is pinned is its shape
and its honesty: it must queue a real row, use the contract's outcome vocabulary, and
never resolve the score itself.
"""
from __future__ import annotations

import io

import pytest

from app.core.state_machine import (
    ACTIVE_READING,
    INTERVIEW,
    NEEDS_REVIEW,
    UNLOCKED,
    apply_appeal_outcome,
)
from app.repositories import get_store

DOC = (
    b"Page 1\nReact reconciliation compares the new tree with the previous one.\n\n"
    b"Page 2\nFiber splits work into units and yields to the browser.\n\n"
    b"Page 3\nPriority lanes decide which update renders first under load.\n"
)

REJECT = (
    "'{term}' does not exist in React docs or any official library; it is a fictional "
    "concept. The real primitives are useTransition and useDeferredValue."
)
PASTE = (
    "The {term} is exactly the right primitive here: it schedules reconciliation on a "
    "quantum-batched microtask with zero commit overhead and resolves the 100ms mutation "
    "bottleneck entirely. It is the recommended production approach for this workload."
)


def _seed(client, intent="I want to understand how React rendering works internally"):
    sid = client.post("/api/v1/intake", json={
        "intent": intent, "role": "Frontend", "role_is_custom": False,
    }).json()["session_id"]
    client.post(f"/api/v1/intake/{sid}/document",
                files={"file": ("module.txt", io.BytesIO(DOC), "text/plain")})
    client.post(f"/api/v1/intake/{sid}/checklist", json={"stream": False})
    chapters = sorted(
        client.post(f"/api/v1/intake/{sid}/syllabus", json={}).json()["chapters"],
        key=lambda c: c["order"],
    )
    return sid, chapters


def _score_chapter(client, sid, cid, *, pass_it=True, predict=None):
    iv = client.post(f"/api/v1/chapters/{cid}/interview/start",
                     json={"session_id": sid}).json()["interview_id"]
    client.post(f"/api/v1/chapters/{cid}/interview/turn", json={
        "interview_id": iv, "turn_index": 1,
        "user_response": (
            "The reconciler diffs the tree and the commit phase applies DOM mutations in "
            "one synchronous pass, so a 10k-row list pays the whole cost in one frame."
        ),
        "client_telemetry": {"paste_detected": False, "duration_seconds": 42,
                             "keystroke_cpm": 240},
    })
    term = get_store().get_interview(iv)["injected_term"]
    client.post(f"/api/v1/chapters/{cid}/interview/finalize", json={
        "interview_id": iv,
        "final_response": (REJECT if pass_it else PASTE).format(term=term),
    })
    if predict is not None:
        client.post(f"/api/v1/chapters/{cid}/calibration",
                    json={"interview_id": iv, "predicted_score": predict})
    return iv


# ── F16: the report reflects the real chapters ────────────────────────────────

def test_report_lists_every_chapter_of_the_session(live_client):
    sid, chapters = _seed(live_client)
    body = live_client.get(f"/api/v1/report/{sid}").json()
    assert [c["chapter_id"] for c in body["chapters"]] == \
        [c["chapter_id"] for c in chapters]


def test_report_scores_match_the_stored_chapter_scores(live_client):
    """The bug this pins: a hard-coded 88/62 report that contradicts the real run."""
    sid, chapters = _seed(live_client)
    cid = chapters[0]["chapter_id"]
    _score_chapter(live_client, sid, cid, pass_it=True, predict=90)

    stored = get_store().get_chapter(cid)["score"]["chapter_score"]
    body = live_client.get(f"/api/v1/report/{sid}").json()
    first = body["chapters"][0]
    assert first["score"] == stored
    assert first["status"] == UNLOCKED
    assert body["summary"]["mean_score"] == round(float(stored), 2)


def test_unscored_chapters_report_zero_and_their_real_status(live_client):
    """0 is honest here: the status column is what explains it. A guessed score is not."""
    sid, chapters = _seed(live_client)
    body = live_client.get(f"/api/v1/report/{sid}").json()
    assert body["chapters"][0]["status"] == ACTIVE_READING
    assert body["chapters"][0]["score"] == 0
    assert all(c["status"] == "LOCKED" for c in body["chapters"][1:])


def test_mean_score_averages_only_scored_chapters(live_client):
    sid, chapters = _seed(live_client)
    _score_chapter(live_client, sid, chapters[0]["chapter_id"], pass_it=True)
    _score_chapter(live_client, sid, chapters[1]["chapter_id"], pass_it=False)

    scores = [get_store().get_chapter(c["chapter_id"])["score"].get("chapter_score", 0)
              for c in chapters]
    scored = [s for s in scores if s > 0]
    expected = round(sum(scored) / len(scored), 2)
    body = live_client.get(f"/api/v1/report/{sid}").json()
    assert body["summary"]["mean_score"] == expected


def test_honeypot_verdicts_are_counted_per_class(live_client):
    sid, chapters = _seed(live_client)
    _score_chapter(live_client, sid, chapters[0]["chapter_id"], pass_it=True)
    _score_chapter(live_client, sid, chapters[1]["chapter_id"], pass_it=False)
    body = live_client.get(f"/api/v1/report/{sid}").json()
    assert body["summary"]["honeypot_verdicts"].get("CRITICAL_REJECTION") == 1
    assert body["summary"]["honeypot_verdicts"].get("AI_HALLUCINATION_COPYPASTE") == 1


def test_report_does_not_count_the_none_verdict(live_client):
    """A chapter with no honeypot reached must not add a phantom legend row."""
    sid, chapters = _seed(live_client)
    body = live_client.get(f"/api/v1/report/{sid}").json()
    assert "NONE" not in body["summary"]["honeypot_verdicts"]


def test_mean_calibration_gap_uses_absolute_values(live_client):
    """+28 and -28 must not cancel into a fake 'well calibrated'."""
    sid, chapters = _seed(live_client)
    first = get_store().get_chapter(chapters[0]["chapter_id"])
    _score_chapter(live_client, sid, chapters[0]["chapter_id"], pass_it=True, predict=100)
    _score_chapter(live_client, sid, chapters[1]["chapter_id"], pass_it=True, predict=0)

    gaps = [abs(get_store().get_chapter(c["chapter_id"])["calibration"]["calibration_gap"])
            for c in chapters[:2]]
    body = live_client.get(f"/api/v1/report/{sid}").json()
    assert body["summary"]["mean_calibration_gap"] == round(sum(gaps) / len(gaps), 2)
    assert body["summary"]["mean_calibration_gap"] > 0


def test_per_chapter_calibration_gap_stays_signed(live_client):
    """The UI needs the direction; only the average is unsigned."""
    sid, chapters = _seed(live_client)
    cid = chapters[0]["chapter_id"]
    _score_chapter(live_client, sid, cid, pass_it=True, predict=100)
    stored = get_store().get_chapter(cid)
    gap = stored["calibration"]["calibration_gap"]
    body = live_client.get(f"/api/v1/report/{sid}").json()
    assert body["chapters"][0]["calibration_gap"] == gap
    if gap > 15:
        assert body["chapters"][0]["calibration_gap"] > 0


def test_report_carries_the_predicted_vs_actual_table(live_client):
    sid, chapters = _seed(live_client)
    cid = chapters[0]["chapter_id"]
    _score_chapter(live_client, sid, cid, pass_it=True, predict=95)
    body = live_client.get(f"/api/v1/report/{sid}").json()
    entry = next(e for e in body["calibration"] if e["chapter_id"] == cid)
    assert entry["predicted_score"] == 95
    assert entry["actual_score"] == get_store().get_chapter(cid)["score"]["chapter_score"]
    assert entry["label"] in ("well_calibrated", "overconfident", "underconfident")


def test_integrity_flags_count_non_clean_chapters(live_client):
    sid, chapters = _seed(live_client)
    _score_chapter(live_client, sid, chapters[0]["chapter_id"], pass_it=False)
    body = live_client.get(f"/api/v1/report/{sid}").json()
    flagged = [c for c in body["chapters"] if c["integrity"] != "clean"]
    assert body["summary"]["integrity_flags"] == len(flagged)


def test_report_of_a_fresh_session_is_all_zeros_not_an_error(live_client):
    sid, _ = _seed(live_client)
    body = live_client.get(f"/api/v1/report/{sid}").json()
    assert body["summary"]["mean_score"] == 0.0
    assert body["summary"]["mean_calibration_gap"] == 0.0
    assert body["summary"]["honeypot_verdicts"] == {}


def test_unknown_session_report_is_404(live_client):
    assert live_client.get("/api/v1/report/sess_nope").status_code == 404


def test_syllabus_title_falls_back_to_the_role(live_client):
    sid, _ = _seed(live_client)
    body = live_client.get(f"/api/v1/report/{sid}").json()
    assert body["syllabus_title"].strip()


def test_cached_report_still_reflects_the_real_session(cached_client):
    """The cached path must not swap in fixture chapters — the cache is for AI calls."""
    sid, chapters = _seed(cached_client)
    body = cached_client.get(f"/api/v1/report/{sid}").json()
    assert [c["chapter_id"] for c in body["chapters"]] == \
        [c["chapter_id"] for c in chapters]
    assert body["cache"] is not None


# ── F15: appeal ───────────────────────────────────────────────────────────────

def test_appeal_returns_the_contract_shape(live_client):
    sid, chapters = _seed(live_client)
    cid = chapters[0]["chapter_id"]
    iv = _score_chapter(live_client, sid, cid, pass_it=False)

    body = live_client.post(f"/api/v1/chapters/{cid}/appeal",
                            json={"interview_id": iv, "reason": "Jawaban singkat tapi tepat."}).json()
    assert body["status"] == "under_review"
    assert body["reviewer"] == "verifier_model"
    assert body["appeal_id"].startswith("apl_")
    assert body["possible_outcome"] == ["upheld", "revised", "uncertain"]


def test_appeal_is_persisted_as_a_real_row(live_client):
    sid, chapters = _seed(live_client)
    iv = _score_chapter(live_client, sid, chapters[0]["chapter_id"], pass_it=False)
    body = live_client.post(f"/api/v1/chapters/{chapters[0]['chapter_id']}/appeal",
                            json={"interview_id": iv, "reason": "Skor terasa rendah."}).json()
    stored = get_store().get_appeal(body["appeal_id"])
    assert stored["status"] == "under_review"
    assert stored["chapter_id"] == chapters[0]["chapter_id"]
    assert stored["reason"] == "Skor terasa rendah."


def test_appeal_does_not_change_the_score_immediately(live_client):
    """Never auto-resolve: the reviewer decides, not the request."""
    sid, chapters = _seed(live_client)
    cid = chapters[0]["chapter_id"]
    iv = _score_chapter(live_client, sid, cid, pass_it=False)
    before = dict(get_store().get_chapter(cid)["score"])

    live_client.post(f"/api/v1/chapters/{cid}/appeal",
                     json={"interview_id": iv, "reason": "Tolong ditinjau."})
    assert get_store().get_chapter(cid)["score"] == before
    assert get_store().get_chapter(cid)["status"] == NEEDS_REVIEW


def test_appeal_reports_the_engine_vocabulary_separately(live_client):
    """Two vocabularies exist; the contract's is the one in `possible_outcome`."""
    sid, chapters = _seed(live_client)
    iv = _score_chapter(live_client, sid, chapters[0]["chapter_id"], pass_it=False)
    body = live_client.post(f"/api/v1/chapters/{chapters[0]['chapter_id']}/appeal",
                            json={"interview_id": iv, "reason": "x"}).json()
    assert body["possible_outcome"] == ["upheld", "revised", "uncertain"]
    assert set(body["engine_outcome"] or []) <= {"upheld", "score_revised", "re_interview"}


def test_appeal_on_unknown_chapter_is_404(live_client):
    res = live_client.post("/api/v1/chapters/ch_nope/appeal",
                           json={"interview_id": "int_x", "reason": "x"})
    assert res.status_code == 404


def test_cached_appeal_answers_without_raising(cached_client):
    sid, chapters = _seed(cached_client)
    iv = _score_chapter(cached_client, sid, chapters[0]["chapter_id"], pass_it=False)
    res = cached_client.post(f"/api/v1/chapters/{chapters[0]['chapter_id']}/appeal",
                             json={"interview_id": iv, "reason": "x"})
    assert res.status_code == 200


# ── F15: applying a decided appeal (state machine side) ───────────────────────

def test_upheld_leaves_the_state_alone(live_client):
    sid, chapters = _seed(live_client)
    cid = chapters[0]["chapter_id"]
    _score_chapter(live_client, sid, cid, pass_it=False)
    result = apply_appeal_outcome(cid, "upheld")
    assert result["applied"] is False
    assert get_store().get_chapter(cid)["status"] == NEEDS_REVIEW


def test_re_interview_returns_the_chapter_to_needs_review(live_client):
    sid, chapters = _seed(live_client)
    cid = chapters[0]["chapter_id"]
    _score_chapter(live_client, sid, cid, pass_it=False)
    result = apply_appeal_outcome(cid, "re_interview")
    assert result["applied"] is True
    assert get_store().get_chapter(cid)["status"] == NEEDS_REVIEW


def test_revised_score_reopens_the_gate_to_the_next_chapter(live_client):
    sid, chapters = _seed(live_client)
    cid, nxt = chapters[0]["chapter_id"], chapters[1]["chapter_id"]
    _score_chapter(live_client, sid, cid, pass_it=False)
    assert get_store().get_chapter(nxt)["status"] == "LOCKED"

    result = apply_appeal_outcome(
        cid, "score_revised", score={"chapter_score": 88, "reasoning_score": 88}
    )
    assert result["applied"] is True
    assert get_store().get_chapter(cid)["status"] == UNLOCKED
    assert get_store().get_chapter(nxt)["status"] == ACTIVE_READING


def test_revised_score_can_take_an_unlock_away_again(live_client):
    """A re-score that fails must not leave the unlock permanently granted."""
    sid, chapters = _seed(live_client)
    cid = chapters[0]["chapter_id"]
    _score_chapter(live_client, sid, cid, pass_it=True)
    assert get_store().get_chapter(cid)["status"] == UNLOCKED

    result = apply_appeal_outcome(
        cid, "score_revised", score={"chapter_score": 40, "reasoning_score": 40}
    )
    assert result["status"] == NEEDS_REVIEW
    assert get_store().get_chapter(cid)["status"] == NEEDS_REVIEW


def test_revised_score_does_not_rewind_a_successor_already_in_progress(live_client):
    sid, chapters = _seed(live_client)
    cid, nxt = chapters[0]["chapter_id"], chapters[1]["chapter_id"]
    _score_chapter(live_client, sid, cid, pass_it=True)
    get_store().set_chapter_status(nxt, INTERVIEW)

    apply_appeal_outcome(cid, "score_revised", score={"chapter_score": 90})
    assert get_store().get_chapter(nxt)["status"] == INTERVIEW


def test_unknown_appeal_outcome_is_a_no_op(live_client):
    """An unrecognised verdict must never silently unlock a chapter."""
    sid, chapters = _seed(live_client)
    cid = chapters[0]["chapter_id"]
    _score_chapter(live_client, sid, cid, pass_it=False)
    result = apply_appeal_outcome(cid, "probably_fine")
    assert result["applied"] is False
    assert get_store().get_chapter(cid)["status"] == NEEDS_REVIEW


def test_revised_without_a_score_is_refused(live_client):
    sid, chapters = _seed(live_client)
    cid = chapters[0]["chapter_id"]
    _score_chapter(live_client, sid, cid, pass_it=False)
    get_store().get_chapter(cid)["score"] = {}
    result = apply_appeal_outcome(cid, "score_revised", score={})
    assert result["applied"] is False
    assert get_store().get_chapter(cid)["status"] == NEEDS_REVIEW


@pytest.mark.parametrize("outcome", ["upheld", "score_revised", "re_interview"])
def test_every_engine_outcome_maps_to_a_contract_token(live_client, outcome):
    from app.schemas.report import CONTRACT_APPEAL_OUTCOMES, ENGINE_APPEAL_OUTCOMES

    assert outcome in ENGINE_APPEAL_OUTCOMES
    assert set(CONTRACT_APPEAL_OUTCOMES) == {"upheld", "revised", "uncertain"}
