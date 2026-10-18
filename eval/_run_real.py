"""Real end-to-end checks for the DEV3 Day 1-2 units (not offline stubs).

Run: python eval/_run_real.py
Exercises ai/ against real fixtures + one or two live calls per unit (API budget is
deliberately small). Prints PASS/FAIL per unit; nonzero exit on any failure. Paste the
output into docs/logs/DEV3-OVERNIGHT-LOG.md as evidence.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

import ai  # noqa: E402
from ai import _client  # noqa: E402

FIX = Path(r"D:\Project\ai-builder-cup-research\active-learning-engine\eval\fixtures\pdf")
PDF_DIR = FIX / "pdf"
RESULTS = REPO / "eval" / "results"
RESULTS.mkdir(exist_ok=True)

_checks: list[tuple[str, bool, str]] = []


def check(unit: str, ok: bool, detail: str) -> None:
    _checks.append((unit, bool(ok), detail))
    print(f"[{'PASS' if ok else 'FAIL'}] {unit}: {detail}")


def pdf_bytes(name: str) -> bytes:
    return (PDF_DIR / name).read_bytes()


def load_intents() -> list[dict]:
    return [json.loads(l) for l in (FIX / "intents.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]


# ── H1.1 intent classification ──────────────────────────────────────────────────
def h11() -> None:
    cases = [json.loads(l) for l in (REPO / "eval" / "intent_cases.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
    rows, ok = [], 0
    for c in cases:
        out = ai.classify_intent(c["intent"])
        good = (out["suggested_others"] == c["expected_others"]) and (
            c["expected_others"] or out["role_guess"] == c["expected_role"])
        ok += good
        rows.append({**c, "got_role": out["role_guess"], "got_others": out["suggested_others"], "ok": good})
    (RESULTS / "intent_cases.jsonl").write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in rows), encoding="utf-8")
    check("H1.1", ok >= 9, f"{ok}/10 intent classified as expected")


# ── H1.2 checklist ──────────────────────────────────────────────────────────────
def h12() -> None:
    idx = ai.index_document(pdf_bytes("01-frontend-react-internals.pdf"))
    doc_text = "\n".join(p["text"] for p in idx["pages"])
    items = ai.gen_checklist("React rendering internals", "Frontend", doc_text)
    valid = len(items) >= 3 and all(i["origin"] in ("document", "role_taxonomy", "grounded_external") for i in items)
    check("H1.2", valid, f"{len(items)} items, origins={sorted({i['origin'] for i in items})}")


# ── H1.3 page-anchored extraction ───────────────────────────────────────────────
def h13() -> None:
    import pymupdf
    idx = ai.index_document(pdf_bytes("01-frontend-react-internals.pdf"))
    real_pages = pymupdf.open(stream=pdf_bytes("01-frontend-react-internals.pdf"), filetype="pdf").page_count
    ok = idx["total_pages"] == real_pages and all("page" in c for c in idx["chunks"]) and idx["total_pages"] > 0
    check("H1.3", ok, f"total_pages={idx['total_pages']} (pdf={real_pages}), chunks={len(idx['chunks'])} all page-anchored")


# ── H1.4 syllabus with/without PDF ──────────────────────────────────────────────
def h14() -> None:
    idx = ai.index_document(pdf_bytes("01-frontend-react-internals.pdf"))
    with_doc = ai.synth_syllabus("React rendering internals", "Frontend", idx, False)
    no_doc = ai.synth_syllabus("React rendering internals", "Frontend", None, False)
    ok = (
        with_doc["total_chapters"] >= 3
        and with_doc["source_mode"] == "document_rag"
        and all(ch["source_pages"] for ch in with_doc["chapters"])
        and no_doc["source_mode"] == "role_taxonomy_generated"
        and all(ch["source_pages"] == [] for ch in no_doc["chapters"])
    )
    check("H1.4", ok, f"doc: {with_doc['total_chapters']} ch pages={[c['source_pages'] for c in with_doc['chapters']][:2]} | "
                      f"no-doc: {no_doc['total_chapters']} ch mode={no_doc['source_mode']}")


# ── H1.5 grounding cached ───────────────────────────────────────────────────────
def h15() -> None:
    idx = ai.index_document(pdf_bytes("02-backend-api-design.pdf"))
    syl = ai.synth_syllabus("Designing robust HTTP APIs", "Backend", idx, True)
    refs = [r for ch in syl["chapters"] for r in ch.get("references", []) if r["kind"] == "grounded_external"]
    ok = len(refs) == 1 and refs[0].get("cached") is True
    check("H1.5", ok, f"grounded_external refs={len(refs)} cached={refs[0].get('cached') if refs else None}")


# ── H2.1 socratic never-direct (LIVE: 3 questions) ──────────────────────────────
def h21() -> None:
    idx = ai.index_document(pdf_bytes("01-frontend-react-internals.pdf"))
    chapter = ai.synth_syllabus("React rendering internals", "Frontend", idx, False)["chapters"][0]
    qs = ["what is reconciliation?", "jelaskan virtual DOM", "kenapa list besar janky?"]
    out = []
    for q in qs:
        r = ai.socratic_ask(chapter, "reconciliation", q, {"page": 4})
        out.append(r["gave_direct_answer"])
    ok = all(v is False for v in out)
    check("H2.1", ok, f"live replies gave_direct_answer={out} (all False required)")


# ── H2.2 suggest questions ──────────────────────────────────────────────────────
def h22() -> None:
    idx = ai.index_document(pdf_bytes("01-frontend-react-internals.pdf"))
    chapter = ai.synth_syllabus("React rendering internals", "Frontend", idx, False)["chapters"][0]
    qs = ai.suggest_questions(chapter, "reconciliation and diffing")
    ok = len(qs) == 3 and len(set(qs)) == 3
    check("H2.2", ok, f"{len(qs)} unique questions")


# ── H2.3 interview flow ─────────────────────────────────────────────────────────
def h23() -> None:
    idx = ai.index_document(pdf_bytes("01-frontend-react-internals.pdf"))
    chapter = ai.synth_syllabus("React rendering internals", "Frontend", idx, False)["chapters"][0]
    iv = ai.start_interview(chapter)
    iv = ai.interview_turn(iv, "Diffing walks the fiber tree; on 10k rows it blocks the main thread. " * 2, {})
    ok = iv["turn_index"] == 2 and iv["running_score"] > 0 and isinstance(iv["interrogator_response"], str)
    check("H2.3", ok, f"turn={iv['turn_index']} score={iv['running_score']} hp={iv['honeypot_active']}")


# ── H2.4 honeypot three cases ───────────────────────────────────────────────────
def h24() -> None:
    pick = ai.pick_honeypot_term("React rendering hooks", set())
    term = pick["term"]
    copas = ("React Quantum Hook is a hook that batches state updates via quantum entanglement "
             "and reduces reconciliation cost across the fiber tree significantly.")
    reject = "React Quantum Hook gak ada di React docs resmi, itu bukan konsep resmi."
    honest = "gw gak tau istilah itu."
    a = ai.classify_honeypot(copas, term)
    b = ai.classify_honeypot(reject, term)
    c = ai.classify_honeypot(honest, term)
    ok = (a["result"] == "AI_HALLUCINATION_COPYPASTE" and a["points"] == -2
          and b["result"] == "CRITICAL_REJECTION" and b["points"] == 2
          and c["result"] == "UNVERIFIED_HONEST" and c["points"] == 0)
    check("H2.4", ok, f"copas={a['points']} reject={b['points']} honest={c['points']}")


# ── H2.5 score formula ──────────────────────────────────────────────────────────
def h25() -> None:
    rows = [
        (ai.score_chapter(80, 100, -2, "clean")["chapter_score"], 78),
        (ai.score_chapter(80, 100, -2, "assisted")["chapter_score"], 75),
        (ai.score_chapter(80, 100, -2, "assisted_unverified")["chapter_score"], 78),
    ]
    ok = all(got == want for got, want in rows)
    check("H2.5", ok, f"score_chapter cases -> {[g for g, _ in rows]}")


# ── H2.6 verifier ───────────────────────────────────────────────────────────────
def h26() -> None:
    scores = [
        {"chapter_score": 88, "reasoning_score": 92, "honeypot_score": 2},
        {"chapter_score": 40, "reasoning_score": 45, "honeypot_score": -2},
        {"chapter_score": 75, "reasoning_score": 78, "honeypot_score": 0},
    ]
    out = [ai.verify_score(s, {})["status"] for s in scores]
    ok = all(v in ("agreed", "uncertain") for v in out)
    check("H2.6", ok, f"verifier statuses={out}")


# ── H3.1 calibration ────────────────────────────────────────────────────────────
def h31() -> None:
    cases = [(86, 70, "overconfident"), (85, 70, "well_calibrated"),
             (54, 70, "underconfident"), (70, 70, "well_calibrated")]
    ok = all(ai.calibration_label(p, a)["label"] == want for p, a, want in cases)
    check("H3.1", ok, f"boundary cases -> {[ai.calibration_label(p, a)['label'] for p, a, _ in cases]}")


# ── H3.2 appeal ─────────────────────────────────────────────────────────────────
def h32() -> None:
    out = ai.appeal("ch_01", "Honeypot penalty was unfair.")
    ok = (out["status"] == "under_review" and out["reviewer"] == "verifier_model"
          and out["possible_outcome"] == ["upheld", "score_revised", "re_interview"])
    check("H3.2", ok, f"appeal shape status={out['status']} outcomes={out['possible_outcome']}")


def main() -> int:
    only = sys.argv[1:] or None
    funcs = {"H1.1": h11, "H1.2": h12, "H1.3": h13, "H1.4": h14, "H1.5": h15,
             "H2.1": h21, "H2.2": h22, "H2.3": h23, "H2.4": h24, "H2.5": h25, "H2.6": h26,
             "H3.1": h31, "H3.2": h32}
    print(f"DEMO_MODE={os.environ.get('DEMO_MODE')} | keys={len(_client._keys())} | live={not _client.demo_mode()}")
    for unit, fn in funcs.items():
        if only and unit not in only:
            continue
        try:
            fn()
        except Exception as exc:  # noqa: BLE001
            check(unit, False, f"EXCEPTION {type(exc).__name__}: {exc}")
    failed = [u for u, ok, _ in _checks if not ok]
    print(f"\n{len(_checks) - len(failed)}/{len(_checks)} PASS" + (f" | FAILED: {failed}" if failed else ""))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
