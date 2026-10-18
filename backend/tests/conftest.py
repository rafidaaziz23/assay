"""Shared pytest fixtures.

Every test runs offline by default: ``DEMO_MODE=cached`` is forced before the app is
imported, so no test can reach Gemini (root conftest.py does the same for the repo's
other suites). The store is reset between tests — it is process-wide, and a leaked
session would silently change what a later test sees.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

os.environ["DEMO_MODE"] = "cached"

# Make ``app`` importable and let the app import the repo-root ``ai`` engine package.
_BACKEND = Path(__file__).resolve().parents[1]
_REPO = _BACKEND.parent
for path in (str(_BACKEND), str(_REPO)):
    if path not in sys.path:
        sys.path.insert(0, path)

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app.main import app  # noqa: E402
from app.repositories import get_store  # noqa: E402


@pytest.fixture(autouse=True)
def clean_store(monkeypatch):
    """Fresh store per test, and a clean environment for the demo-mode triggers."""
    store = get_store()
    store.reset()
    # Hard guard: the suite must never make a real model call, whichever code path a
    # test exercises. ``ai/_client._keys()`` reads these at call time, so removing them
    # from the process environment is enough to force the deterministic path.
    for name in ("GOOGLE_API_KEY", "GOOGLE_API_KEY_FALLBACK", "GOOGLE_API_KEY_FALLBACK_2"):
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setenv("DEMO_MODE", "cached")
    yield store
    store.reset()


@pytest.fixture()
def client() -> TestClient:
    """Plain JSON client: no demo header, so the *live* code paths stay testable."""
    return TestClient(app)


@pytest.fixture()
def frontend_client() -> TestClient:
    """Alias kept for readability — same plain client the UI uses for JSON calls."""
    return TestClient(app)


@pytest.fixture()
def cached_client() -> TestClient:
    """Client that mirrors the demo: ``x-demo-mode: cached`` on every request."""
    return TestClient(app, headers={"x-demo-mode": "cached"})


@pytest.fixture()
def live_client(monkeypatch) -> TestClient:
    """Client on the live code path: ``DEMO_MODE=live`` and no demo header.

    The cached scenarios intercept *every* endpoint when DEMO_MODE is cached, so tests
    of the real classifier/scoring logic would silently assert against the frozen
    fixture instead. This fixture forces the live route. The suite's autouse fixture
    removes the model keys from the environment, so "live" here means the bound *code
    path*, never a real network call: every AI call resolves to its deterministic
    fallback.
    """
    monkeypatch.setenv("DEMO_MODE", "live")
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
    monkeypatch.delenv("GOOGLE_API_KEY_FALLBACK", raising=False)
    monkeypatch.delenv("GOOGLE_API_KEY_FALLBACK_2", raising=False)
    return TestClient(app)


INTAKE_BODY = {
    "intent": "I want to understand how React rendering works internally",
    "role": "Frontend",
    "role_is_custom": False,
}


@pytest.fixture()
def session_id(frontend_client) -> str:
    res = frontend_client.post("/api/v1/intake", json=INTAKE_BODY)
    assert res.status_code == 201, res.text
    return res.json()["session_id"]


@pytest.fixture()
def chapters(frontend_client, session_id):
    """A synthesized syllabus, returning its chapter list."""
    frontend_client.post(f"/api/v1/intake/{session_id}/checklist", json={"stream": False})
    res = frontend_client.post(f"/api/v1/intake/{session_id}/syllabus", json={})
    assert res.status_code == 201, res.text
    return res.json()["chapters"]
