"""F17 — Cached fallback with two scenarios.

This is the feature the recording runs on. DEV 2 calls it the most critical backend
feature, and the reason is simple: the whole 3-minute video goes through this path, so a
fallback that raises, drifts between takes, or silently reaches for the network fails the
demo for reasons that have nothing to do with the AI.

What is pinned:

* **All three triggers** work: ``DEMO_MODE=cached``, ``x-demo-mode: cached``, and a Gemini
  429/500/503. A trigger that only fires in one of the three is the bug that shows up
  on stage.
* **No endpoint raises anywhere on the cached path.** Exercised by walking every endpoint,
  not by trusting that each one remembered its envelope.
* **The two scenarios are distinct and frozen**: ``success`` ends in CRITICAL_REJECTION
  with a pass; ``caught`` ends in AI_HALLUCINATION_COPYPASTE with a drop. Recorded twice
  in a row, byte-identical.
* **The envelope is uniform** — ``fallback_active`` / ``source`` / ``message`` — because
  the frontend's FallbackBadge reads exactly those keys.
* **R7 self-check** reports the cache is structurally consistent with the current schema.
"""
from __future__ import annotations

import io

import pytest
from fastapi.testclient import TestClient

from app.core import fallback as fb
from app.main import app
from app.repositories import get_store

DOC = (
    b"Page 1\nReact reconciliation compares the new tree with the previous one.\n\n"
    b"Page 2\nFiber splits work into units and yields to the browser.\n\n"
    b"Page 3\nPriority lanes decide which update renders first under load.\n"
)

ENVELOPE_KEYS = {"fallback_active", "source", "message"}


def _seed(client):
    sid = client.post("/api/v1/intake", json={
        "intent": "I want to understand how React rendering works internally",
        "role": "Frontend", "role_is_custom": False,
    }).json()["session_id"]
    client.post(f"/api/v1/intake/{sid}/document",
                files={"file": ("module.txt", io.BytesIO(DOC), "text/plain")})
    return sid


def _walk_to_finalize(client, sid, *, reject=True, scenario=None):
    suffix = f"?scenario={scenario}" if scenario else ""
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
        "user_response": "The reconciler diffs the tree and commits DOM mutations in one pass.",
    })
    term = get_store().get_interview(iv)["injected_term"]
    text = (f"'{term}' does not exist in React docs; it is fictional."
            if reject else
            f"The {term} is the right primitive and removes all commit overhead in production.")
    finalize = client.post(f"/api/v1/chapters/{cid}/interview/finalize{suffix}",
                           json={"interview_id": iv, "final_response": text}).json()
    return cid, iv, finalize


# ── the three triggers ────────────────────────────────────────────────────────

def test_env_trigger_activates_the_cache(monkeypatch):
    monkeypatch.setenv("DEMO_MODE", "cached")
    assert fb.demo_mode_active() is True


def test_header_trigger_activates_the_cache():
    assert fb.demo_mode_active("cached") is True


def test_header_trigger_wins_even_when_env_is_live(monkeypatch):
    monkeypatch.setenv("DEMO_MODE", "live")
    assert fb.demo_mode_active("cached") is True


def test_env_live_without_header_stays_live(monkeypatch):
    monkeypatch.setenv("DEMO_MODE", "live")
    assert fb.demo_mode_active() is False


def test_runtime_env_change_is_seen_even_though_settings_was_built_at_import(monkeypatch):
    """settings is an import-time snapshot; reading it alone is how a demo makes live calls."""
    monkeypatch.setenv("DEMO_MODE", "cached")
    assert fb.demo_mode_active() is True
    monkeypatch.setenv("DEMO_MODE", "live")
    assert fb.demo_mode_active() is False


@pytest.mark.parametrize("code", [429, 500, 503])
def test_gemini_error_statuses_are_fallback_triggers(code):
    assert fb.gemini_error_is_fallback(code) is True


@pytest.mark.parametrize("code", [400, 401, 404, None])
def test_non_trigger_statuses_are_not_swallowed(code):
    """Only 429/500/503 degrade. A 400 is a bug in our own request and must be visible."""
    assert fb.gemini_error_is_fallback(code) is False


def test_middleware_advertises_the_resilience_mode(cached_client):
    res = cached_client.get("/health")
    assert res.headers.get("X-Assay-Resilience-Mode") == fb.FALLBACK_SOURCE


def test_middleware_does_not_mislabel_a_live_request(live_client):
    res = live_client.get("/health")
    assert "X-Assay-Resilience-Mode" not in res.headers


# ── the two scenarios ─────────────────────────────────────────────────────────

def test_success_scenario_ends_in_critical_rejection_and_passes(cached_client):
    sid = _seed(cached_client)
    _, _, finalize = _walk_to_finalize(cached_client, sid, reject=True)
    assert finalize["honeypot_verdict"]["result"] == "CRITICAL_REJECTION"
    assert finalize["passed"] is True
    assert finalize["chapter_state_update"]["current_chapter_status"] == "UNLOCKED"
    assert finalize["score"]["chapter_score"] >= 75


def test_caught_scenario_ends_in_copypaste_and_fails(cached_client):
    sid = _seed(cached_client)
    _, _, finalize = _walk_to_finalize(cached_client, sid, reject=False, scenario="caught")
    assert finalize["honeypot_verdict"]["result"] == "AI_HALLUCINATION_COPYPASTE"
    assert finalize["passed"] is False
    assert finalize["chapter_state_update"]["current_chapter_status"] == "NEEDS_REVIEW"
    assert finalize["score"]["honeypot_score"] < 0


def test_the_two_scenarios_are_actually_different():
    success = fb.cached_finalize("success")
    caught = fb.cached_finalize("caught")
    assert success["result"] != caught["result"]
    assert success["reasoning_score"] > caught["reasoning_score"]
    assert success["integrity_flag"] == "clean"
    assert caught["integrity_flag"] != "clean"


def test_success_scenario_serves_a_clean_integrity_state(cached_client):
    sid = _seed(cached_client)
    _, _, finalize = _walk_to_finalize(cached_client, sid, reject=True)
    assert finalize["integrity_flag"] == "clean"


def test_caught_scenario_publishes_focus_events_for_the_report(cached_client):
    """The caught beat needs integrity content, or the report's log is empty on camera."""
    sid = _seed(cached_client)
    cid, iv, finalize = _walk_to_finalize(cached_client, sid, reject=False, scenario="caught")
    assert get_store().get_focus_events(iv)
    assert finalize["integrity_flag"] in ("assisted", "assisted_unverified")
    report = cached_client.get(f"/api/v1/report/{sid}").json()
    assert report["summary"]["integrity_flags"] >= 1


def test_explicit_scenario_query_selects_the_caught_beat(monkeypatch):
    monkeypatch.setenv("DEMO_MODE", "cached")
    assert fb.active_scenario(None, "caught") == "caught"
    assert fb.active_scenario(None, "success") == "success"


def test_unknown_scenario_falls_back_to_the_default_instead_of_erroring():
    assert fb.active_scenario("cached", "nonsense") == fb.DEFAULT_SCENARIO


def test_unknown_scenario_from_the_header_is_ignored(monkeypatch):
    """A garbage header alone must not activate the cache; only the exact token does."""
    monkeypatch.setenv("DEMO_MODE", "live")
    assert fb.active_scenario("garbage") is None
    assert fb.active_scenario("cached") == fb.DEFAULT_SCENARIO


def test_unknown_header_scenario_with_cache_already_on_uses_the_default(monkeypatch):
    monkeypatch.setenv("DEMO_MODE", "cached")
    assert fb.active_scenario("garbage") == fb.DEFAULT_SCENARIO


# ── determinism across takes ──────────────────────────────────────────────────

def test_finalize_is_byte_identical_on_two_consecutive_runs(cached_client):
    a = _walk_to_finalize(cached_client, _seed(cached_client), reject=True)[2]
    b = _walk_to_finalize(cached_client, _seed(cached_client), reject=True)[2]
    assert a["honeypot_verdict"] == b["honeypot_verdict"]
    assert a["score"] == b["score"]
    assert a["verifier"] == b["verifier"]


def test_recording_does_not_depend_on_what_the_student_typed(cached_client):
    """Different final answers must still produce the scripted verdict on the cached path."""
    sid_a = _seed(cached_client)
    sid_b = _seed(cached_client)
    a = _walk_to_finalize(cached_client, sid_a, reject=True)[2]
    b = _walk_to_finalize(cached_client, sid_b, reject=False)[2]
    assert a["honeypot_verdict"]["result"] == b["honeypot_verdict"]["result"] == \
        "CRITICAL_REJECTION"


# ── no endpoint raises on the cached path ─────────────────────────────────────

def test_every_endpoint_answers_and_carries_the_envelope_when_cached(cached_client):
    """The golden rule is "no blank spinners": every AI-backed reply needs the envelope."""
    sid = _seed(cached_client)
    checklist = cached_client.post(f"/api/v1/intake/{sid}/checklist", json={"stream": False})
    assert checklist.status_code == 200
    chapters = sorted(
        cached_client.post(f"/api/v1/intake/{sid}/syllabus", json={}).json()["chapters"],
        key=lambda c: c["order"],
    )
    cid = chapters[0]["chapter_id"]

    reader = cached_client.get(f"/api/v1/chapters/{cid}")
    assert reader.status_code == 200
    assert reader.json()["content_markdown"].strip()

    ask = cached_client.post(f"/api/v1/chapters/{cid}/ask", json={
        "session_id": sid, "selected_text": "the reconciler", "question": "how does it scale?",
        "anchor": {"page": 1, "char_start": 0, "char_end": 20},
    })
    assert ask.status_code == 200
    body = ask.json()
    assert body["reply"].strip()
    assert ENVELOPE_KEYS <= set(body["fallback"])
    # The cached reply is still a question — the thesis must not invert on the fallback.
    assert body["gave_direct_answer"] is False
    assert "?" in body["reply"]

    start = cached_client.post(f"/api/v1/chapters/{cid}/interview/start",
                               json={"session_id": sid})
    assert start.status_code == 200
    assert start.json()["first_question"].strip()

    focus = cached_client.post(f"/api/v1/chapters/{cid}/focus-events", json={
        "interview_id": "int_x", "events": [{"type": "TAB_BLUR", "at_ms": 1}],
    })
    assert focus.status_code == 200
    assert ENVELOPE_KEYS <= set(focus.json()["fallback"])


def test_finalize_envelope_matches_the_contract(cached_client):
    sid = _seed(cached_client)
    _, _, finalize = _walk_to_finalize(cached_client, sid)
    assert ENVELOPE_KEYS <= set(finalize["fallback"])
    assert finalize["fallback"]["source"] == "LOCAL_DETERMINISTIC_CACHE"
    assert finalize["fallback"]["fallback_active"] is True
    assert finalize["cache"]["cache"]["schema_version"] == fb.CACHE_SCHEMA_VERSION


def test_cached_content_is_non_empty_for_every_chapter(cached_client):
    """A blank chapter on the reader page is a blank spinner with extra steps."""
    sid = _seed(cached_client)
    chapters = sorted(
        cached_client.post(f"/api/v1/intake/{sid}/syllabus", json={}).json()["chapters"],
        key=lambda c: c["order"],
    )
    for chapter in chapters:
        body = cached_client.get(f"/api/v1/chapters/{chapter['chapter_id']}").json()
        assert body["content_markdown"].strip(), chapter["chapter_id"]
        assert body["source_pages"], chapter["chapter_id"]


def test_cached_grounding_never_raises_on_a_miss():
    hit = fb.cached_grounding("react-internals")
    miss = fb.cached_grounding("some topic nobody cached")
    assert hit["references"]
    assert miss["references"], "a miss must still cite something citable"
    assert miss["cached"] is True


# ── R7 self-check ─────────────────────────────────────────────────────────────

def test_cache_self_check_reports_ok():
    report = fb.validate_cache()
    assert report["ok"] is True, report["problems"]
    assert report["scenarios"] == ["success", "caught"]
    assert report["cache_schema_version"] == fb.CACHE_SCHEMA_VERSION


def test_cache_self_check_is_exposed_over_http(cached_client):
    body = cached_client.get("/health/cache").json()
    assert body["ok"] is True
    assert body["problems"] == []


def test_health_reports_the_live_env_not_the_import_time_snapshot(monkeypatch):
    """/health has no header to read, so it must reflect the environment right now."""
    monkeypatch.setenv("DEMO_MODE", "cached")
    assert TestClient(app).get("/health").json()["demo_mode"] == "cached"
    monkeypatch.setenv("DEMO_MODE", "live")
    assert TestClient(app).get("/health").json()["demo_mode"] == "live"

    # settings was built at import and still says whatever .env said; the endpoint must
    # not be reporting that value.
    from app.config import settings

    assert settings is not None


def test_cache_self_check_catches_a_broken_scenario(monkeypatch):
    """The check has to be able to fail, or it is decoration."""
    broken = {sid: dict(scene) for sid, scene in fb.SCENARIOS.items()}
    broken["caught"] = {**broken["caught"], "checklist": []}
    monkeypatch.setattr(fb, "SCENARIOS", broken)

    report = fb.validate_cache()
    assert report["ok"] is False
    assert any("caught" in problem for problem in report["problems"])
