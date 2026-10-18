"""F2 — Realtime checklist generation + edit (DEV 2 breakdown F2).

Contract under test: ``POST /api/v1/intake/:sessionId/checklist`` (JSON and SSE) and
``PUT`` the same path.

Rules that must hold:
* One endpoint, two modes: ``{"stream": true}`` -> SSE with ``checklist.partial`` per
  item closed by ``checklist.done``; no flag -> one complete JSON body.
* ``origin`` is a required enum: ``document | role_taxonomy | grounded_external``.
* ``PUT`` rewrites the ``selected`` flags and ONLY selected items become the syllabus
  basis (F3 consumes them).
"""
from __future__ import annotations

import json

from app.repositories import get_store


def _start(frontend_client, role: str = "Frontend") -> str:
    res = frontend_client.post("/api/v1/intake", json={
        "intent": "I want to understand how React rendering works internally",
        "role": role,
        "role_is_custom": False,
    })
    return res.json()["session_id"]


# ── JSON mode ──────────────────────────────────────────────────────────────────

def test_checklist_json_shape(frontend_client):
    sid = _start(frontend_client)
    res = frontend_client.post(f"/api/v1/intake/{sid}/checklist", json={"stream": False})
    assert res.status_code == 200
    body = res.json()
    assert body["session_id"] == sid
    assert body["role"] == "Frontend"
    assert body["checklist"], "checklist must not be empty"
    for item in body["checklist"]:
        assert set(item) >= {"item_id", "topic", "selected", "confidence", "origin"}
        assert item["origin"] in ("document", "role_taxonomy", "grounded_external")
        assert 0.0 <= item["confidence"] <= 1.0


def test_checklist_default_request_body_is_optional(frontend_client):
    """An empty body must still generate: the frontend sends no payload at all."""
    sid = _start(frontend_client)
    assert frontend_client.post(f"/api/v1/intake/{sid}/checklist").status_code == 200


def test_checklist_origin_is_role_taxonomy_without_document(frontend_client):
    """No upload -> nothing may claim `document` grounding.

    The cached demo fixture is pre-baked assuming an upload, so it tags items
    `document`; serving that verbatim without a document would be a false claim of
    grounding, and the honeypot's whole argument rests on that anchor being real.
    `grounded_external` is legitimate either way — external search grounding does not
    depend on the upload.
    """
    sid = _start(frontend_client)
    body = frontend_client.post(f"/api/v1/intake/{sid}/checklist", json={}).json()
    assert body["source"] == "role_taxonomy"
    assert all(i["origin"] != "document" for i in body["checklist"])
    assert {i["origin"] for i in body["checklist"]} <= {
        "role_taxonomy", "grounded_external"
    }


def test_checklist_source_reports_document_when_uploaded(frontend_client, clean_store):
    """With a document indexed, the source says so and document grounding is labelled."""
    sid = _start(frontend_client)
    clean_store.update_session(sid, has_document=True, doc_index={
        "pages": [{"page": 1, "text": "React reconciliation and fiber scheduling"}],
        "total_pages": 1, "document_name": "react.pdf",
    })
    body = frontend_client.post(f"/api/v1/intake/{sid}/checklist", json={}).json()
    assert body["source"] == "document+role"
    origins = {i["origin"] for i in body["checklist"]}
    assert origins <= {"document", "role_taxonomy", "grounded_external"}
    # Mixed origins are a feature (document + taxonomy enrichment), not a bug.
    assert "document" in origins


def test_checklist_does_not_leak_internal_proposal_marker(frontend_client):
    """`proposed_selected` is internal bookkeeping, not part of the contract."""
    sid = _start(frontend_client)
    body = frontend_client.post(f"/api/v1/intake/{sid}/checklist", json={}).json()
    assert all("proposed_selected" not in i for i in body["checklist"])


def test_checklist_is_persisted_on_the_session(frontend_client, clean_store):
    sid = _start(frontend_client)
    body = frontend_client.post(f"/api/v1/intake/{sid}/checklist", json={}).json()
    stored = clean_store.get_session(sid)["checklist"]
    assert [i["item_id"] for i in stored] == [i["item_id"] for i in body["checklist"]]
    assert clean_store.get_session(sid)["status"] == "CHECKLIST"


def test_checklist_unknown_session_is_404(frontend_client):
    res = frontend_client.post("/api/v1/intake/sess_nope/checklist", json={})
    assert res.status_code == 404


# ── SSE mode ───────────────────────────────────────────────────────────────────

def _parse_sse(raw: str):
    """Split an SSE stream into (event, data) pairs.

    Normalises CRLF first: starlette writes ``\\r\\n`` separators, and splitting on
    ``\\n\\n`` alone would collapse the whole stream into one block.
    """
    events = []
    for block in raw.replace("\r\n", "\n").split("\n\n"):
        event, data = None, []
        for line in block.splitlines():
            if line.startswith("event:"):
                event = line.split(":", 1)[1].strip()
            elif line.startswith("data:"):
                data.append(line.split(":", 1)[1].strip())
        if event:
            events.append((event, "\n".join(data)))
    return events


def test_checklist_stream_emits_partial_then_done(frontend_client):
    """SSE is the recorded moment; a buffered response would break the video (F2 risk)."""
    sid = _start(frontend_client)
    with frontend_client.stream(
        "POST", f"/api/v1/intake/{sid}/checklist", json={"stream": True}
    ) as response:
        assert response.status_code == 200
        assert "text/event-stream" in response.headers["content-type"]
        raw = "".join(response.iter_text())

    events = _parse_sse(raw)
    names = [name for name, _ in events]
    assert names.count("checklist.partial") >= 3
    assert names[-1] == "checklist.done"

    items = [json.loads(data) for name, data in events if name == "checklist.partial"]
    for item in items:
        assert item["item_id"] and item["topic"]
        assert item["origin"] in ("document", "role_taxonomy", "grounded_external")

    done = json.loads([data for name, data in events if name == "checklist.done"][0])
    assert done["status"] == "complete"
    assert done["total"] == len(items)


def test_checklist_stream_persists_items(frontend_client, clean_store):
    sid = _start(frontend_client)
    with frontend_client.stream(
        "POST", f"/api/v1/intake/{sid}/checklist", json={"stream": True}
    ) as response:
        "".join(response.iter_text())
    assert clean_store.get_session(sid)["checklist"], "SSE run must persist too"


# ── PUT selection ──────────────────────────────────────────────────────────────

def test_put_selection_rewrites_flags(frontend_client):
    sid = _start(frontend_client)
    body = frontend_client.post(f"/api/v1/intake/{sid}/checklist", json={}).json()
    ids = [i["item_id"] for i in body["checklist"]]
    keep = ids[:2]
    drop = ids[2:]

    res = frontend_client.put(
        f"/api/v1/intake/{sid}/checklist", json={"selected_item_ids": keep}
    )
    assert res.status_code == 200
    updated = res.json()
    assert updated["selected_item_ids"] == keep
    assert updated["selected_count"] == len(keep)

    by_id = {i["item_id"]: i for i in updated["checklist"]}
    assert all(by_id[i]["selected"] for i in keep)
    assert all(not by_id[i]["selected"] for i in drop)


def test_put_selection_only_selected_feed_the_syllabus(frontend_client, clean_store):
    """F3 consumes `selected` items; anything unchecked must not reach it."""
    sid = _start(frontend_client)
    body = frontend_client.post(f"/api/v1/intake/{sid}/checklist", json={}).json()
    keep = [body["checklist"][0]["item_id"]]
    frontend_client.put(f"/api/v1/intake/{sid}/checklist", json={"selected_item_ids": keep})

    selected = clean_store.selected_checklist_items(sid)
    assert [i["item_id"] for i in selected] == keep
    assert all(i["selected"] for i in selected)


def test_put_marks_dropped_items_as_elective(frontend_client):
    """DEV 2 addition: the UI can show 'proposed then dropped' (app_addons).

    Only items the ENGINE proposed as selected can become `elective`; an item that was
    already unchecked at generation was never part of the proposal.
    """
    sid = _start(frontend_client)
    body = frontend_client.post(f"/api/v1/intake/{sid}/checklist", json={}).json()
    proposed = [i["item_id"] for i in body["checklist"] if i["selected"]]
    dropped = proposed[1:]
    assert dropped, "fixture needs at least two selected items"

    res = frontend_client.put(
        f"/api/v1/intake/{sid}/checklist", json={"selected_item_ids": proposed[:1]}
    ).json()
    by_id = {i["item_id"]: i for i in res["checklist"]}
    assert by_id[proposed[0]]["elective"] is False
    assert all(by_id[i]["elective"] is True for i in dropped)
    # Never-proposed items stay non-elective.
    for item in body["checklist"]:
        if not item["selected"]:
            assert by_id[item["item_id"]]["elective"] is False


def test_put_empty_selection_is_allowed(frontend_client):
    """Unchecking everything is a legitimate choice, not a validation error."""
    sid = _start(frontend_client)
    frontend_client.post(f"/api/v1/intake/{sid}/checklist", json={}).json()
    res = frontend_client.put(
        f"/api/v1/intake/{sid}/checklist", json={"selected_item_ids": []}
    )
    assert res.status_code == 200
    assert res.json()["selected_count"] == 0


def test_put_unknown_item_id_is_422(frontend_client):
    sid = _start(frontend_client)
    frontend_client.post(f"/api/v1/intake/{sid}/checklist", json={}).json()
    res = frontend_client.put(
        f"/api/v1/intake/{sid}/checklist", json={"selected_item_ids": ["ck_999"]}
    )
    assert res.status_code == 422


def test_put_before_generate_is_409(frontend_client):
    """Selecting items that do not exist yet must not silently 'succeed'."""
    sid = _start(frontend_client)
    res = frontend_client.put(
        f"/api/v1/intake/{sid}/checklist", json={"selected_item_ids": ["ck_01"]}
    )
    assert res.status_code == 409


# ── F17 envelope in cached mode ────────────────────────────────────────────────

def test_checklist_carries_fallback_envelope_when_cached(cached_client):
    """The demo badge reads this: LOCAL_DETERMINISTIC_CACHE + scenario."""
    res = cached_client.post("/api/v1/intake", json={
        "intent": "I want to understand how React rendering works internally",
        "role": "Frontend",
    })
    sid = res.json()["session_id"]
    body = cached_client.post(f"/api/v1/intake/{sid}/checklist", json={}).json()
    assert body["cache"]["fallback_active"] is True
    assert body["cache"]["source"] == "LOCAL_DETERMINISTIC_CACHE"
    assert body["cache"]["scenario"] in ("success", "caught")
    assert body["engine"] == "deterministic_cache"


def test_checklist_has_no_fallback_envelope_in_live_mode(frontend_client, monkeypatch):
    """DEMO_MODE=live and no demo header -> a real (engine) response, no envelope."""
    monkeypatch.setenv("DEMO_MODE", "live")
    res = frontend_client.post("/api/v1/intake", json={
        "intent": "I want to understand how React rendering works internally",
        "role": "Frontend",
    })
    sid = res.json()["session_id"]
    body = frontend_client.post(f"/api/v1/intake/{sid}/checklist", json={}).json()
    assert body["cache"] is None
    assert body["engine"] == "live"


def test_demo_header_alone_activates_the_cache(frontend_client):
    """Trigger #2 in API-CONTRACTS section 3: header, independent of the env var."""
    res = frontend_client.post(
        "/api/v1/intake",
        json={"intent": "I want to understand how React rendering works internally",
              "role": "Frontend"},
        headers={"x-demo-mode": "cached"},
    )
    sid = res.json()["session_id"]
    body = frontend_client.post(
        f"/api/v1/intake/{sid}/checklist", json={}, headers={"x-demo-mode": "cached"}
    ).json()
    assert body["cache"]["scenario"] == "success"
    assert body["engine"] == "deterministic_cache"


def test_store_is_reset_between_tests(clean_store):
    """Guard the guard: a leaked session would let later tests pass on stale state."""
    assert clean_store.sessions == {}
    assert get_store().chapters == {}
