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
    assert get_res.json()["model"] in ("gemini-2.5-flash", "gemini-flash-lite-latest")

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
