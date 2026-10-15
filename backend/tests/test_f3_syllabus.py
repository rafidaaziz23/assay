"""F3/F4/F5 — syllabus synthesis, page-anchored ingest, grounding cache.

Contract under test: ``POST /api/v1/intake/:sessionId/syllabus`` plus the ingest and
retrieval endpoints DEV 2 owns.

Rules that must hold:
* F3 — the store normalises DEV 3's chunking into the section 2.3 schema and seeds the
  state machine: ``order=1`` -> ACTIVE_READING, the rest LOCKED. The no-PDF path MUST
  still produce chapters, marked ``role_taxonomy_generated`` (Hari 1 gate).
* F4 — ingest keeps page numbers. Every ``source_pages`` anchor must point at a real
  page of the upload; an invented page number is how the honeypot claim becomes
  unverifiable.
* F5 — external grounding touches one chapter only and is served cached.
"""
from __future__ import annotations

import io

from app.repositories import get_store


def _start(frontend_client, document=None) -> str:
    res = frontend_client.post("/api/v1/intake", json={
        "intent": "I want to understand how React rendering works internally",
        "role": "Frontend",
        "role_is_custom": False,
        "document": document,
    })
    return res.json()["session_id"]


def _upload(frontend_client, sid: str, payload, name: str = "module.txt",
            content_type: str = "text/plain"):
    """Upload a document. ``payload`` may be ``str`` (encoded as UTF-8) or raw ``bytes``
    (for a real PDF, which must NOT be re-encoded)."""
    body = payload.encode() if isinstance(payload, str) else payload
    return frontend_client.post(
        f"/api/v1/intake/{sid}/document",
        files={"file": (name, io.BytesIO(body), content_type)},
    )


REACT_DOC = (
    "Page 1\n"
    "React reconciliation compares the new element tree with the previous one.\n\n"
    "Page 2\n"
    "The Fiber reconciler splits work into units and yields to the browser.\n\n"
    "Page 3\n"
    "Priority lanes decide which update is rendered first under load.\n"
)


# ── F3: no-PDF path ────────────────────────────────────────────────────────────

def test_syllabus_without_document_still_produces_chapters(frontend_client):
    """The Hari 1 gate: no upload must not mean no syllabus."""
    sid = _start(frontend_client)
    frontend_client.post(f"/api/v1/intake/{sid}/checklist", json={})
    res = frontend_client.post(f"/api/v1/intake/{sid}/syllabus", json={})
    assert res.status_code == 201
    body = res.json()
    assert body["source_mode"] == "role_taxonomy_generated"
    assert body["total_chapters"] >= 3
    assert body["total_chapters"] == len(body["chapters"])


def test_syllabus_chapter_schema_is_complete(frontend_client):
    sid = _start(frontend_client)
    frontend_client.post(f"/api/v1/intake/{sid}/checklist", json={})
    chapters = frontend_client.post(
        f"/api/v1/intake/{sid}/syllabus", json={}
    ).json()["chapters"]
    for ch in chapters:
        assert set(ch) >= {
            "chapter_id", "title", "order", "status", "prerequisites",
            "estimated_reading_minutes", "source_pages", "references",
        }
        assert ch["title"]
        assert ch["estimated_reading_minutes"] > 0


def test_syllabus_seeds_state_machine_reading_locked_split(frontend_client, clean_store):
    sid = _start(frontend_client)
    frontend_client.post(f"/api/v1/intake/{sid}/checklist", json={})
    chapters = frontend_client.post(
        f"/api/v1/intake/{sid}/syllabus", json={}
    ).json()["chapters"]

    ordered = sorted(chapters, key=lambda c: c["order"])
    assert ordered[0]["status"] == "ACTIVE_READING"
    assert all(c["status"] == "LOCKED" for c in ordered[1:])

    first = clean_store.get_chapter(ordered[0]["chapter_id"])
    second = clean_store.get_chapter(ordered[1]["chapter_id"])
    assert first["status"] == "ACTIVE_READING"
    assert second["status"] == "LOCKED"
    # next_locked is stored, not recomputed per request (DEV 2 section 3, reason 4).
    assert first["next_locked"] is True
    assert second["next_locked"] is True


def test_syllabus_prerequisites_chain_in_order(frontend_client):
    sid = _start(frontend_client)
    frontend_client.post(f"/api/v1/intake/{sid}/checklist", json={})
    chapters = sorted(
        frontend_client.post(f"/api/v1/intake/{sid}/syllabus", json={}).json()["chapters"],
        key=lambda c: c["order"],
    )
    assert chapters[0]["prerequisites"] == []
    for prev, cur in zip(chapters, chapters[1:]):
        assert prev["chapter_id"] in cur["prerequisites"]


def test_syllabus_uses_only_selected_checklist_items(frontend_client, clean_store):
    """F2 -> F3 handoff: unchecked topics must not become chapters.

    The demo fixture always yields the same chapter ids, so the assertion is on the
    stored selection the syllabus was built from, not on chapter count.
    """
    sid = _start(frontend_client)
    body = frontend_client.post(f"/api/v1/intake/{sid}/checklist", json={}).json()
    keep = [body["checklist"][0]["item_id"]]
    frontend_client.put(f"/api/v1/intake/{sid}/checklist", json={"selected_item_ids": keep})
    frontend_client.post(f"/api/v1/intake/{sid}/syllabus", json={})

    selected = clean_store.selected_checklist_items(sid)
    assert [i["item_id"] for i in selected] == keep


def test_syllabus_unknown_session_is_404(frontend_client):
    res = frontend_client.post("/api/v1/intake/sess_missing/syllabus", json={})
    assert res.status_code == 404


def test_syllabus_marks_session_status(frontend_client, clean_store):
    sid = _start(frontend_client)
    frontend_client.post(f"/api/v1/intake/{sid}/checklist", json={})
    body = frontend_client.post(f"/api/v1/intake/{sid}/syllabus", json={}).json()
    session = clean_store.get_session(sid)
    assert session["status"] == "SYLLABUS"
    assert session["syllabus_id"] == body["syllabus_id"]
    assert session["syllabus_title"] == body["title"]


def test_syllabus_chapters_carry_renderable_content(frontend_client, clean_store):
    """DEMO-SCRIPT golden rule 1: the reader must never render an empty chapter."""
    sid = _start(frontend_client)
    frontend_client.post(f"/api/v1/intake/{sid}/checklist", json={})
    chapters = frontend_client.post(
        f"/api/v1/intake/{sid}/syllabus", json={}
    ).json()["chapters"]
    for ch in chapters:
        assert clean_store.get_chapter(ch["chapter_id"])["content_markdown"].strip()


# ── F4: page-anchored ingest ───────────────────────────────────────────────────

def test_upload_text_document_keeps_page_numbers(frontend_client):
    """Losing page numbers kills the honeypot's verifiability claim (F4)."""
    sid = _start(frontend_client)
    res = _upload(frontend_client, sid, REACT_DOC)
    assert res.status_code == 201
    body = res.json()
    assert body["pages"] == [1, 2, 3]
    assert body["total_pages"] == 3
    assert body["source_mode"] == "document_rag"


def test_upload_text_without_markers_is_one_honest_page(frontend_client):
    """No fabricated pagination: an unmarked upload is one page, not three guesses."""
    sid = _start(frontend_client)
    body = _upload(frontend_client, sid, "React reconciliation in one paragraph.").json()
    assert body["pages"] == [1]
    assert body["total_pages"] == 1


def test_upload_marks_session_as_document_backed(frontend_client, clean_store):
    sid = _start(frontend_client)
    _upload(frontend_client, sid, REACT_DOC)
    session = clean_store.get_session(sid)
    assert session["has_document"] is True
    assert session["source_mode"] == "document_rag"
    assert session["doc_index"]["total_pages"] == 3


def test_upload_binary_pdf_is_handled(frontend_client):
    """A corrupt/unreadable PDF still yields an ingest result, not a 500."""
    sid = _start(frontend_client)
    res = frontend_client.post(
        f"/api/v1/intake/{sid}/document",
        files={"file": ("broken.pdf", io.BytesIO(b"%PDF-1.4 not really a pdf"),
                        "application/pdf")},
    )
    assert res.status_code == 201
    assert res.json()["total_pages"] >= 1


def test_upload_unknown_session_is_404(frontend_client):
    res = _upload(frontend_client, "sess_nope", REACT_DOC)
    assert res.status_code == 404


def test_document_retrieval_returns_page_anchors(frontend_client):
    """Retrieval must return {page, char_start, char_end} for /chapters/:id/ask (F4)."""
    sid = _start(frontend_client)
    _upload(frontend_client, sid, REACT_DOC)
    res = frontend_client.get(f"/api/v1/intake/{sid}/document")
    assert res.status_code == 200
    body = res.json()
    assert body["total_pages"] == 3
    for page in body["pages"]:
        assert set(page) >= {"page", "char_start", "char_end", "text"}
        assert page["char_end"] >= page["char_start"]
        assert page["text"]


def test_document_retrieval_single_page(frontend_client):
    sid = _start(frontend_client)
    _upload(frontend_client, sid, REACT_DOC)
    body = frontend_client.get(f"/api/v1/intake/{sid}/document?page=2").json()
    assert [p["page"] for p in body["pages"]] == [2]
    assert "Fiber" in body["pages"][0]["text"]


def test_document_retrieval_missing_page_is_404(frontend_client):
    sid = _start(frontend_client)
    _upload(frontend_client, sid, REACT_DOC)
    assert frontend_client.get(
        f"/api/v1/intake/{sid}/document?page=99"
    ).status_code == 404


def test_syllabus_source_mode_follows_the_upload(frontend_client):
    sid = _start(frontend_client)
    _upload(frontend_client, sid, REACT_DOC)
    frontend_client.post(f"/api/v1/intake/{sid}/checklist", json={})
    body = frontend_client.post(f"/api/v1/intake/{sid}/syllabus", json={}).json()
    assert body["source_mode"] == "document_rag"


def test_source_pages_are_real_pages_of_the_upload(frontend_client):
    """An anchor outside the document is an unverifiable claim (F4)."""
    sid = _start(frontend_client)
    _upload(frontend_client, sid, REACT_DOC)
    frontend_client.post(f"/api/v1/intake/{sid}/checklist", json={})
    chapters = frontend_client.post(
        f"/api/v1/intake/{sid}/syllabus", json={}
    ).json()["chapters"]
    real = {1, 2, 3}
    for ch in chapters:
        assert set(ch["source_pages"]) <= real, ch
        assert ch["source_pages"], "each chapter needs at least one anchor"


def test_syllabus_references_are_document_kind_with_a_page(frontend_client):
    sid = _start(frontend_client)
    _upload(frontend_client, sid, REACT_DOC)
    frontend_client.post(f"/api/v1/intake/{sid}/checklist", json={})
    chapters = frontend_client.post(
        f"/api/v1/intake/{sid}/syllabus", json={}
    ).json()["chapters"]
    doc_refs = [r for ch in chapters for r in ch["references"] if r["kind"] == "document"]
    assert doc_refs, "PDF-RAG is mandatory: at least one document reference"
    for ref in doc_refs:
        assert ref["page"] in {1, 2, 3}
        assert ref["verified"] is True


# ── F5: grounding cache ────────────────────────────────────────────────────────

def test_grounding_touches_only_one_chapter_and_is_cached(frontend_client):
    """Trimmed to 1 chapter (WBS section 1) and served from cache."""
    sid = _start(frontend_client)
    _upload(frontend_client, sid, REACT_DOC)
    frontend_client.post(f"/api/v1/intake/{sid}/checklist", json={})
    body = frontend_client.post(
        f"/api/v1/intake/{sid}/syllabus", json={"enable_search_grounding": True}
    ).json()
    chapters = sorted(body["chapters"], key=lambda c: c["order"])
    grounded = [ch for ch in chapters if any(
        r["kind"] == "grounded_external" for r in ch["references"]
    )]
    assert len(grounded) == 1
    assert grounded[0]["order"] == 1
    assert all(r.get("cached") is True for r in grounded[0]["references"]
               if r["kind"] == "grounded_external")
    assert body["grounding"]["cached"] is True


def test_grounding_is_off_by_default(frontend_client):
    sid = _start(frontend_client)
    _upload(frontend_client, sid, REACT_DOC)
    frontend_client.post(f"/api/v1/intake/{sid}/checklist", json={})
    body = frontend_client.post(f"/api/v1/intake/{sid}/syllabus", json={}).json()
    assert all(
        r["kind"] != "grounded_external"
        for ch in body["chapters"] for r in ch["references"]
    )
    assert body["grounding"] is None


def test_grounding_cache_never_raises_on_a_miss():
    from app.core.fallback import cached_grounding

    hit = cached_grounding("topic that is not cached")
    assert hit["cached"] is True
    # A miss still serves a citable reference: grounding is on for the recorded beat,
    # and an empty panel would read as a broken feature on camera.
    assert hit["references"]
    assert all(r["kind"] == "grounded_external" and r["cached"] for r in hit["references"])


def test_cached_mode_syllabus_still_returns_chapters(cached_client):
    res = cached_client.post("/api/v1/intake", json={
        "intent": "I want to understand how React rendering works internally",
        "role": "Frontend",
    })
    sid = res.json()["session_id"]
    cached_client.post(f"/api/v1/intake/{sid}/checklist", json={})
    body = cached_client.post(f"/api/v1/intake/{sid}/syllabus", json={}).json()
    assert body["total_chapters"] >= 2
    assert body["cache"]["scenario"] in ("success", "caught")


def test_cache_fixture_is_self_consistent():
    """R7 self-check: a stale cache is what silently breaks the recording."""
    from app.core.fallback import validate_cache

    report = validate_cache()
    assert report["ok"] is True, report["problems"]
    assert set(report["scenarios"]) == {"success", "caught"}


def test_store_reset_between_tests_holds(clean_store):
    assert clean_store.sessions == {}
    assert get_store().chapters == {}


# ── F4 — real PDF, end to end through the DEV 3 engine ────────────────────────
# The suite previously only exercised a CORRUPT PDF (the fallback path). The success path
# — a real multi-page PDF going through ai.index_document — was never tested, so a
# regression that merged every page into one blob would have passed CI and only shown up
# when someone uploaded a real module on stage.

def _build_pdf(page_texts):
    """A genuine multi-page PDF, built with the same library the engine uses."""
    import fitz

    doc = fitz.open()
    for index, text in enumerate(page_texts, 1):
        page = doc.new_page()
        page.insert_text((72, 100), f"Page {index}")
        page.insert_text((72, 140), text)
    pdf_bytes = doc.tobytes()
    doc.close()
    return pdf_bytes


PDF_PAGES = [
    "React reconciliation compares the new virtual tree against the previous one.",
    "Fiber splits rendering work into units and yields control back to the browser.",
    "Priority lanes decide which state update renders first under heavy load.",
    "The commit phase applies all pending DOM mutations in one synchronous pass.",
]


def test_real_pdf_is_split_into_one_entry_per_page(live_client):
    """Page separation is the product's load-bearing claim: the honeypot verdict says
    "this term appears on no page of your document", which is unverifiable if ingest
    collapses the PDF into a single blob."""
    sid = _start(live_client)
    res = _upload(live_client, sid, _build_pdf(PDF_PAGES), name="module.pdf",
                  content_type="application/pdf")
    assert res.status_code == 201, res.text

    body = res.json()
    assert body["total_pages"] == len(PDF_PAGES)
    assert body["pages"] == [1, 2, 3, 4]
    assert body["char_count"] > 0


def test_real_pdf_text_stays_isolated_per_page(live_client):
    """Each page must carry its OWN text. A merged blob would still pass a page-count
    assertion, so the content has to be checked, not just the number."""
    sid = _start(live_client)
    _upload(live_client, sid, _build_pdf(PDF_PAGES), name="module.pdf",
            content_type="application/pdf")

    pages = get_store().get_session(sid)["doc_index"]["pages"]
    assert [p["page"] for p in pages] == [1, 2, 3, 4]
    for index, stored in enumerate(pages):
        assert PDF_PAGES[index].split()[0] in stored["text"], stored
        # No page may contain a sentence that belongs to another page.
        for other in PDF_PAGES:
            if other != PDF_PAGES[index]:
                assert other not in stored["text"]


def test_real_pdf_pages_are_addressable_by_retrieval(live_client):
    """The {page, char_start, char_end} anchor is what /ask cites; it only works if the
    ingest really kept per-page offsets."""
    sid = _start(live_client)
    _upload(live_client, sid, _build_pdf(PDF_PAGES), name="module.pdf",
            content_type="application/pdf")

    res = live_client.get(f"/api/v1/intake/{sid}/document?page=3")
    assert res.status_code == 200
    entry = res.json()["pages"][0]
    assert entry["page"] == 3
    assert entry["char_start"] == 0
    assert entry["char_end"] == len(entry["text"])
    assert PDF_PAGES[2].split()[0] in entry["text"]


def test_real_pdf_drives_the_syllabus_anchors(live_client):
    """A 4-page module must produce chapters anchored across those 4 real pages, not all
    pointing at page 1."""
    sid = _start(live_client)
    _upload(live_client, sid, _build_pdf(PDF_PAGES), name="module.pdf",
            content_type="application/pdf")
    live_client.post(f"/api/v1/intake/{sid}/checklist", json={})
    syllabus = live_client.post(f"/api/v1/intake/{sid}/syllabus", json={}).json()
    assert syllabus["source_mode"] == "document_rag"

    anchored = [p for ch in syllabus["chapters"] for p in (ch.get("source_pages") or [])]
    assert anchored, "chapters carried no page anchors despite a document upload"
    assert set(anchored) <= {1, 2, 3, 4}


def test_real_pdf_upload_reports_a_consistent_engine_label(live_client, cached_client):
    """The label used to be hardcoded "live", which claimed live extraction inside a
    cached run. Ingest is local work, but the label must still agree with the mode."""
    sid = _start(live_client)
    live = _upload(live_client, sid, _build_pdf(PDF_PAGES), name="module.pdf",
                   content_type="application/pdf").json()
    assert live["engine"] == "live"

    sid2 = _start(cached_client)
    cached = _upload(cached_client, sid2, _build_pdf(PDF_PAGES), name="module.pdf",
                     content_type="application/pdf").json()
    assert cached["engine"] == "deterministic_cache"
    # The extraction itself is real on both paths — only the label changes.
    assert cached["total_pages"] == len(PDF_PAGES)


def test_pdf_fallback_keeps_key_names_the_engine_uses():
    """Key drift between `ai.index_document` (page/text) and the fallback was a real
    KeyError that only fired when the engine failed — i.e. when a demo was already
    under stress."""
    from app.services.pdf_service import extract_pages_from_pdf_bytes

    pages = extract_pages_from_pdf_bytes(b"not a pdf at all")
    assert pages and set(pages[0]) == {"page", "text", "char_count"}
