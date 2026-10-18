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
    assert data["name"] == "Maya Lin"
    assert data["institution"] == "Stanford University"


def test_dashboard_summary():
    res = client.get("/api/v1/dashboard/summary")
    assert res.status_code == 200
    data = res.json()
    assert data["learner_name"] == "Maya Lin"
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
