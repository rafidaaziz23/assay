"""RAG retrieval metrics over the fixture corpus (DEV3-ROADMAP section 7).

Metrics:
  page_hit_rate      — fraction of gold questions whose expected pages intersect the
                       pages a chapter's source_pages would cover for that doc.
  recall@k           — fraction of answerable gold questions whose expected page appears
                       in the top-k retrieved pages (lexical scoring, no model).
  refusal_accuracy   — for unanswerable questions, the retriever must return NO page
                       (target 2/2, no fabrication).

Ground truth lives in the fixture `_manifest.json` / `gold_resolved.jsonl`. Never
hand-edit gold pages; re-run the fixture build if layout changes.

Run: python eval/run_rag.py
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

FIX = Path(r"D:\Project\ai-builder-cup-research\active-learning-engine\eval\fixtures\pdf")
PDF_DIR = FIX / "pdf"
RESULTS = REPO / "eval" / "results"
RESULTS.mkdir(exist_ok=True)

_STOP = {"the", "a", "an", "of", "to", "in", "is", "how", "what", "why", "and", "or",
         "does", "do", "for", "on", "with", "it", "that", "this", "are", "be", "can"}


def _terms(text: str) -> list[str]:
    return [w for w in re.findall(r"[a-z0-9]+", (text or "").lower()) if w not in _STOP and len(w) > 2]


def _load_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    return [json.loads(l) for l in path.read_text(encoding="utf-8").splitlines() if l.strip()]


def _page_map() -> dict:
    p = PDF_DIR / "_page_map.json"
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}


def _doc_pages(doc: str) -> dict[int, str]:
    """{page_number: text} for one fixture PDF."""
    import pymupdf
    path = PDF_DIR / doc
    if not path.exists():
        return {}
    pdf = pymupdf.open(path)
    out = {i: (page.get_text() or "") for i, page in enumerate(pdf, 1)}
    pdf.close()
    return out


def retrieve(question: str, pages: dict[int, str], k: int = 3) -> list[int]:
    """Lexical top-k pages for a question (deterministic, no model)."""
    q = set(_terms(question))
    scored = []
    for page, text in pages.items():
        words = set(_terms(text))
        overlap = len(q & words)
        if overlap:
            scored.append((overlap, -page, page))
    scored.sort(reverse=True)
    return [p for _s, _n, p in scored[:k]]


def _refuse_live(question: str, doc_text: str) -> bool | None:
    """Model retrieval gate: does the document contain the answer? None if offline."""
    from ai import _client
    prompt = (
        "You are a strict retrieval gate. Answer ONLY from the document below. "
        "If the document does NOT contain the information needed to answer the question, "
        "reply with exactly REFUSE. Otherwise reply with exactly ANSWER.\n"
        f"Question: {question}\nDocument:\n{doc_text[:6000]}"
    )
    out = _client.generate(prompt)
    if out is None:
        return None
    return (out or "").strip().upper().startswith("REFUSE")


def _refuse_lexical(question: str, pages: dict[int, str]) -> bool:
    """Offline fallback: refuse when the question's distinctive terms are absent."""
    q = set(_terms(question))
    present: set[str] = set()
    for t in pages.values():
        present.update(_terms(t))
    absent = len(q - present) / len(q) if q else 1.0
    best = max((len(q & set(_terms(t))) for t in pages.values()), default=0)
    return best < 4 and absent >= 0.5


def main() -> int:
    gold = _load_jsonl(PDF_DIR / "gold_resolved.jsonl") or _load_jsonl(FIX / "gold.jsonl")
    if not gold:
        print("no gold questions found — run the fixture build first")
        return 1

    # group gold by document
    by_doc: dict[str, list[dict]] = {}
    for g in gold:
        doc = g.get("doc") or g.get("pdf") or g.get("document")
        if doc:
            by_doc.setdefault(doc, []).append(g)

    page_cache: dict[str, dict[int, str]] = {}
    hits = total = 0
    unanswerable_total = unanswerable_refused = 0
    page_hit_hits = page_hit_total = 0

    for doc, questions in by_doc.items():
        pages = page_cache.setdefault(doc, _doc_pages(doc))
        if not pages:
            continue
        for q in questions:
            question = q.get("question") or q.get("q") or ""
            expected = q.get("gold_pages") or q.get("pages") or q.get("expected_pages") or []
            answerable = q.get("answerable", True) and bool(expected)
            if not answerable:
                unanswerable_total += 1
                doc_text = "\n".join(pages.values())
                live = _refuse_live(question, doc_text)
                refused = live if live is not None else _refuse_lexical(question, pages)
                if refused:
                    unanswerable_refused += 1
                continue
            total += 1
            got = retrieve(question, pages, k=3)
            if set(got) & set(expected):
                hits += 1
            page_hit_total += 1
            if set(got[:1]) & set(expected):
                page_hit_hits += 1

    recall = hits / total if total else 0.0
    page_hit = page_hit_hits / page_hit_total if page_hit_total else 0.0
    refusal = unanswerable_refused / unanswerable_total if unanswerable_total else 0.0

    report = {
        "answerable_questions": total,
        "recall_at_3": round(recall, 3),
        "page_hit_rate_at_1": round(page_hit, 3),
        "unanswerable_questions": unanswerable_total,
        "refusal_accuracy": round(refusal, 3),
    }
    (RESULTS / "rag_metrics.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print("RAG metrics (lexical retrieval; refusal via model gate):")
    for k, v in report.items():
        print(f"  {k}: {v}")
    print(f"\nwrote {RESULTS / 'rag_metrics.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
