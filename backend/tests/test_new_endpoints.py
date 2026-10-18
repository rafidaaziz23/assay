"""Tests for new Assay API endpoints: Auth, Dashboard Summary, and Settings."""
from __future__ import annotations
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_auth_login_success():
    res = client.post(
        "/api/v1/auth/login",
        json={"email": "maya.lin@stanford.edu", "password": "secretpassword", "remember": True},
    )
    assert res.status_code == 200
    data = res.json()
    assert "access_token" in data
    assert data["user"]["name"] == "Maya Lin"
    assert data["user"]["role"] == "Fellow"
    assert data["user"]["streak_days"] == 14


def test_auth_me_returns_profile():
    res = client.get("/api/v1/auth/me")
    assert res.status_code == 200
    data = res.json()
    assert data["name"] in ("Maya Lin", "Rafida Aziz")


def test_dashboard_summary():
    res = client.get("/api/v1/dashboard/summary")
    assert res.status_code == 200
    data = res.json()
    assert data["learner_name"] in ("Maya Lin", "Rafida Aziz")
    assert data["active_subjects_count"] == 3
    assert data["defenses_passed_count"] == 12
    assert len(data["learning_paths"]) >= 2
    assert len(data["recent_inquiries"]) >= 3
    assert data["upcoming_defense"]["examiner_name"] == "Dr. Julian Vance"


def test_settings_get_and_post():
    get_res = client.get("/api/v1/settings")
    assert get_res.status_code == 200
    # Default must be a live model ID: gemini-2.5-flash now returns 404
    # NOT_FOUND ("no longer available to new users"). Assert the property, not a
    # literal, so a future model bump does not silently re-break this test.
    assert get_res.json()["model"].startswith("gemini-3")

    update_res = client.post(
        "/api/v1/settings",
        json={
            "model": "claude-3-5-sonnet",
            "rigor": "academic",
            "fallacy_sensitivity": "aggressive",
            "audio_device": "USB Studio Mic",
        },
    )
    assert update_res.status_code == 200
    assert update_res.json()["model"] == "claude-3-5-sonnet"
    assert update_res.json()["fallacy_sensitivity"] == "aggressive"


def test_auth_list_users():
    res = client.get("/api/v1/auth/users")
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    user_names = [u["name"] for u in data]
    assert "Maya Lin" in user_names or "Rafida Aziz" in user_names


def test_notifications_list_and_mark_read():
    res = client.get("/api/v1/notifications")
    assert res.status_code == 200
    notifs = res.json()
    assert isinstance(notifs, list)

    mark_res = client.post("/api/v1/notifications/mark-read")
    assert mark_res.status_code == 200
    assert mark_res.json()["status"] == "ok"


def test_stats_honeypot_copypaste_detected(cached_client):
    """When a candidate pastes an external LLM hallucination about Monotonic Variance Prior."""
    # Seed stats session
    from app.repositories import get_store
    get_store().set_chapter_status("ch_01", "INTERVIEW")
    iv = cached_client.post("/api/v1/chapters/ch_01/interview/start", json={"session_id": "sess_math_stats"}).json()
    
    # Candidate copypastes external LLM hallucination
    copypaste_text = (
        "The Monotonic Variance Prior is an essential mathematical formulation in Neyman-Pearson "
        "testing that guarantees zero Type II error by uniformly constraining parameter divergence."
    )
    res = cached_client.post("/api/v1/chapters/ch_01/interview/finalize", json={
        "interview_id": iv["interview_id"],
        "final_response": copypaste_text,
    })
    assert res.status_code == 200
    data = res.json()
    assert data["honeypot_verdict"]["result"] == "AI_HALLUCINATION_COPYPASTE"
    assert data["honeypot_verdict"]["term"] == "Monotonic Variance Prior"
    assert data["passed"] is False
    assert data["integrity_flag"] == "assisted"
    assert data["fallback"]["scenario"] == "stats_caught"


def test_stats_honeypot_critical_rejection_passes(cached_client):
    """When a candidate identifies Monotonic Variance Prior as fictitious and rejects it."""
    from app.repositories import get_store
    get_store().set_chapter_status("ch_01", "INTERVIEW")
    iv = cached_client.post("/api/v1/chapters/ch_01/interview/start", json={"session_id": "sess_math_stats"}).json()
    
    rejection_text = (
        "The Monotonic Variance Prior is a fictitious concept not found in Neyman-Pearson "
        "theory. In statistical hypothesis testing, Type II error (beta) is strictly bounded "
        "by the critical threshold and sample size, not an arbitrary prior."
    )
    res = cached_client.post("/api/v1/chapters/ch_01/interview/finalize", json={
        "interview_id": iv["interview_id"],
        "final_response": rejection_text,
    })
    assert res.status_code == 200
    data = res.json()
    assert data["honeypot_verdict"]["result"] == "CRITICAL_REJECTION"
    assert data["passed"] is True
    assert data["integrity_flag"] == "clean"
    assert data["fallback"]["scenario"] == "stats_success"


def test_socratic_ask_stats_counter_probe(cached_client):
    """Deep Reader highlighting statistical concepts triggers the Socratic Neyman-Pearson counter-probe."""
    res = cached_client.post("/api/v1/chapters/ch_01/ask", json={
        "session_id": "sess_math_stats",
        "selected_text": "Monotone Likelihood Ratio condition",
        "question": "What does this mean?",
    })
    assert res.status_code == 200
    data = res.json()
    assert data["gave_direct_answer"] is False
    assert "Monotone Likelihood Ratio" in data["reply"]
    assert "adversarial counter-example" in data["reply"]

