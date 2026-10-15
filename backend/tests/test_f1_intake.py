"""F1 — Intake & Role Selector (DEV 2 breakdown F1, ADR 004).

Contract under test: ``GET /api/v1/roles`` and ``POST /api/v1/intake``.

Rules that must hold:
* ``role`` in the 9 seed roles, OR ``"Others"`` + ``role_is_custom: true`` + non-empty
  ``custom_role``. Enforced HERE, in intake, not at classify time (ADR 004 s2.4).
* ``intent`` needs at least 3 words -> 422 otherwise.
* A missing document is not an error: ``has_document: false``.
* ``next`` must point at the checklist endpoint — easy to forget, and the frontend
  navigates with it.
"""
from __future__ import annotations

SEED_ROLES = [
    "Frontend", "Backend", "Fullstack", "DevOps", "Data/ML",
    "Mobile", "QA/Test", "Security", "System Design",
]

INTENT = "I want to understand how React rendering works internally"


# ── GET /roles ─────────────────────────────────────────────────────────────────

def test_roles_returns_all_nine_seeds_and_others(frontend_client):
    res = frontend_client.get("/api/v1/roles")
    assert res.status_code == 200
    body = res.json()
    assert body["roles"] == SEED_ROLES
    assert body["others_option"] == "Others"


def test_roles_are_stable_across_calls(frontend_client):
    """The selector must not reorder between renders."""
    first = frontend_client.get("/api/v1/roles").json()["roles"]
    second = frontend_client.get("/api/v1/roles").json()["roles"]
    assert first == second == SEED_ROLES


# ── POST /intake: happy path ───────────────────────────────────────────────────

def test_intake_seed_role_returns_201_and_next_pointer(frontend_client):
    res = frontend_client.post("/api/v1/intake", json={
        "intent": INTENT, "role": "Frontend", "role_is_custom": False,
    })
    assert res.status_code == 201
    body = res.json()
    assert body["session_id"].startswith("sess_")
    assert body["role"] == "Frontend"
    assert body["has_document"] is False
    assert body["suggested_others"] is False
    assert body["available_roles"] == SEED_ROLES
    assert body["next"] == f"POST /api/v1/intake/{body['session_id']}/checklist"


def test_intake_without_document_is_not_an_error(frontend_client):
    """Empty payload is a valid state, not a 4xx (F1)."""
    res = frontend_client.post("/api/v1/intake", json={
        "intent": INTENT, "role": "Backend",
    })
    assert res.status_code == 201
    assert res.json()["has_document"] is False


def test_intake_session_id_is_unique(frontend_client):
    ids = {
        frontend_client.post("/api/v1/intake", json={
            "intent": INTENT, "role": "Frontend",
        }).json()["session_id"]
        for _ in range(5)
    }
    assert len(ids) == 5


def test_intake_persists_session_for_later_steps(frontend_client, clean_store):
    body = frontend_client.post("/api/v1/intake", json={
        "intent": INTENT, "role": "Frontend",
    }).json()
    stored = clean_store.get_session(body["session_id"])
    assert stored is not None
    assert stored["intent"] == INTENT
    assert stored["role"] == "Frontend"
    assert stored["status"] == "INTAKE"


# ── custom role ("Others") ─────────────────────────────────────────────────────

def test_others_with_custom_role_is_accepted(frontend_client):
    res = frontend_client.post("/api/v1/intake", json={
        "intent": "I want to learn underwater basket weaving architecture",
        "role": "Others", "role_is_custom": True, "custom_role": "Basket Architect",
    })
    assert res.status_code == 201
    body = res.json()
    assert body["suggested_others"] is True
    assert body["role"] == "Basket Architect"


def test_others_without_custom_role_is_coerced_not_rejected(frontend_client, clean_store):
    """ADR 004: an incomplete Others still yields a usable session.

    The demo must not dead-end on a selector edge case; the role degrades to
    ``Others`` rather than 422-ing the whole intake screen.
    """
    res = frontend_client.post("/api/v1/intake", json={
        "intent": INTENT, "role": "Others", "role_is_custom": False,
    })
    assert res.status_code == 201
    body = res.json()
    assert body["role"] == "Others"
    assert body["suggested_others"] is True
    assert clean_store.get_session(body["session_id"])["role"] == "Others"


def test_unknown_role_is_treated_as_others(frontend_client):
    """A role outside the seed set cannot enter as itself."""
    res = frontend_client.post("/api/v1/intake", json={
        "intent": INTENT, "role": "Rocket Surgery", "role_is_custom": False,
    })
    assert res.status_code == 201
    assert res.json()["role"] == "Others"
    assert res.json()["suggested_others"] is True


def test_custom_role_not_duplicated_when_role_field_already_custom(frontend_client):
    """Frontend sends role=custom text with role_is_custom=true in one variant."""
    res = frontend_client.post("/api/v1/intake", json={
        "intent": INTENT, "role": "Basket Architect", "role_is_custom": True,
        "custom_role": "Basket Architect",
    })
    assert res.status_code == 201
    assert res.json()["role"] == "Basket Architect"


# ── validation ─────────────────────────────────────────────────────────────────

def test_intent_under_three_words_is_422(frontend_client):
    res = frontend_client.post("/api/v1/intake", json={
        "intent": "learn React", "role": "Frontend",
    })
    assert res.status_code == 422


def test_missing_intent_is_422(frontend_client):
    res = frontend_client.post("/api/v1/intake", json={"role": "Frontend"})
    assert res.status_code == 422


def test_missing_role_is_422(frontend_client):
    res = frontend_client.post("/api/v1/intake", json={"intent": INTENT})
    assert res.status_code == 422


def test_three_word_intent_is_accepted(frontend_client):
    res = frontend_client.post("/api/v1/intake", json={
        "intent": "learn React internals", "role": "Frontend",
    })
    assert res.status_code == 201


# ── GET /health (deployment smoke) ─────────────────────────────────────────────

def test_health_reports_demo_mode(frontend_client):
    body = frontend_client.get("/health").json()
    assert body["status"] == "healthy"
    assert body["demo_mode"] in ("live", "cached")
