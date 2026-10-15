"""F4 — PDF ingest, page-anchored.

Page numbers are the product's load-bearing claim: the honeypot verdict says "this term
appears on no page of your document". If ingest silently drops pagination, the claim
becomes unverifiable (DEV 2 breakdown F4).

Key naming is frozen to ``page`` / ``text`` / ``char_count`` — the shape
``ai.index_document`` returns and the one the rest of the backend stores. This module
used to emit ``page_number``, which produced a ``KeyError: 'page'`` the moment the
engine path failed and this fallback took over, i.e. exactly when a demo is already
under stress.
"""
from __future__ import annotations

from typing import Any, Dict, List

FALLBACK_TEXT = "Document text could not be extracted; ingest kept the file for reference."


def extract_pages_from_pdf_bytes(pdf_bytes: bytes) -> List[Dict[str, Any]]:
    """Extract text per page with 1-based page numbers.

    Falls back to a single labelled page when PyMuPDF cannot read the stream (corrupt
    file, or a caller that routed non-PDF bytes here). One honest page beats invented
    pagination, and beats a 500 during a live demo.
    """
    pages: List[Dict[str, Any]] = []
    try:
        import fitz  # PyMuPDF

        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        for page_index in range(len(doc)):
            text = (doc[page_index].get_text() or "").strip()
            pages.append({
                "page": page_index + 1,
                "text": text,
                "char_count": len(text),
            })
        doc.close()
    except Exception:
        pages = []

    if not pages:
        return [{"page": 1, "text": FALLBACK_TEXT, "char_count": len(FALLBACK_TEXT)}]
    return pages
