import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"

def test_get_roles():
    response = client.get("/api/v1/roles")
    assert response.status_code == 200
    data = response.json()
    assert "Frontend" in data["roles"]
    assert data["others_option"] == "Others"

def test_intake_creation():
    response = client.post("/api/v1/intake", json={
        "intent": "I want to understand React internals and Fiber architecture",
        "role": "Frontend",
        "role_is_custom": False
    })
    assert response.status_code == 201
    data = response.json()
    assert "session_id" in data
    assert data["role"] == "Frontend"

def test_honeypot_rejection_scoring():
    response = client.post("/api/v1/chapters/ch_01/interview/finalize", json={
        "interview_id": "test_int",
        "final_response": "React Quantum Hook does not exist in React docs. It is a fictional concept."
    })
    assert response.status_code == 200
    data = response.json()
    assert data["honeypot_verdict"]["result"] == "CRITICAL_REJECTION"
    assert data["score"]["honeypot_score"] == 2
    assert data["passed"] is True
