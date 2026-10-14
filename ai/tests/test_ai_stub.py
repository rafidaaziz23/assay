"""Stub-level checks: every public ai/ function returns the contract shape (offline)."""
import ai


def test_classify_intent_shape():
    out = ai.classify_intent("I want to understand how React rendering works internally")
    assert out["role_guess"] == "Frontend"
    assert out["suggested_others"] is False
    assert 0 <= out["confidence"] <= 1


def test_classify_intent_unknown_goes_others():
    out = ai.classify_intent("teach me underwater basket weaving theory")
    assert out["suggested_others"] is True
    assert out["role_guess"] == "Others"


def test_gen_checklist_origins():
    items = ai.gen_checklist("React internals", "Frontend", None)
    assert len(items) >= 3
    for it in items:
        assert set(it) >= {"item_id", "topic", "selected", "confidence", "origin"}
        assert it["origin"] in ("document", "role_taxonomy", "grounded_external")


def test_gen_checklist_stream():
    it = ai.gen_checklist("React internals", "Frontend", None, stream=True)
    assert hasattr(it, "__next__")
    assert next(it)["item_id"]


def test_synth_syllabus_no_doc():
    syl = ai.synth_syllabus("React internals", "Frontend", None, False)
    assert syl["source_mode"] == "role_taxonomy_generated"
    assert syl["total_chapters"] >= 3
    for ch in syl["chapters"]:
        assert ch["source_pages"] == []
        assert ch["title"] and ch["order"] >= 1


def test_socratic_ask_never_direct():
    out = ai.socratic_ask({"title": "Rendering"}, "reconciliation", "what is it?", {"page": 4})
    assert out["gave_direct_answer"] is False
    assert out["mode"] == "socratic"
    assert out["citations"] == [{"kind": "document", "page": 4}]


def test_suggest_questions_three_unique():
    qs = ai.suggest_questions({"title": "Rendering"}, "reconciliation and diffing")
    assert len(qs) == 3
    assert len(set(qs)) == 3


def test_interview_flow_shape():
    iv = ai.start_interview({"chapter_id": "ch_01", "title": "React rendering"})
    assert iv["interview_id"].startswith("int_")
    assert iv["turn_index"] == 1
    assert iv["focus_mode"]["available"] is True

    iv = ai.interview_turn(iv, "VDOM diffing costs CPU on 10k items " * 3, {})
    assert iv["turn_index"] == 2
    assert iv["honeypot_active"] is True
    assert iv["honeypot_metadata"]["source"] == "deterministic_catalog"

    fin = ai.finalize_interview(iv, "React Quantum Hook gak ada di docs resmi.", set())
    assert set(fin["score"]) == {"chapter_score", "reasoning_score", "integrity_score", "honeypot_score"}
    assert fin["honeypot_verdict"]["result"] in ai.CLASS_POINTS
    assert fin["chapter_state_update"]["current_chapter_status"] in ("UNLOCKED", "NEEDS_REVIEW")
    assert fin["verifier"]["status"] in ("agreed", "uncertain")


def test_pick_honeypot_term_and_rotation():
    a = ai.pick_honeypot_term("React rendering hooks", set())
    assert a["source"] == "deterministic_catalog"
    assert a["expected_action"] == "REJECT_AS_FICTITIOUS"
    b = ai.pick_honeypot_term("React rendering hooks", {a["term"]})
    assert b["term"] != a["term"]


def test_classify_honeypot_four_classes():
    copas = ("React Quantum Hook is a hook that uses quantum entanglement to batch state "
             "updates and cut reconciliation cost across the fiber tree.")
    reject = "React Quantum Hook gak ada di React docs resmi, itu bukan konsep resmi."
    honest = "gw gak tau istilah itu."
    evasive = "Menarik, lanjut saja."

    assert ai.classify_honeypot(copas, "React Quantum Hook")["result"] == "AI_HALLUCINATION_COPYPASTE"
    assert ai.classify_honeypot(reject, "React Quantum Hook")["points"] == 2
    assert ai.classify_honeypot(honest, "React Quantum Hook")["points"] == 0
    assert ai.classify_honeypot(evasive, "React Quantum Hook")["points"] == -1


def test_score_chapter_formula():
    assert ai.score_chapter(80, 100, -2, "clean")["chapter_score"] == 78
    assert ai.score_chapter(80, 100, -2, "assisted")["chapter_score"] == 75
    assert ai.score_chapter(80, 100, -2, "assisted_unverified")["chapter_score"] == 78
    assert ai.score_chapter(100, 100, 2, "clean")["chapter_score"] == 100  # clamped
    assert ai.score_chapter(0, 0, -2, "assisted")["chapter_score"] == 0  # clamped


def test_calibration_labels():
    assert ai.calibration_label(90, 88)["label"] == "well_calibrated"
    assert ai.calibration_label(100, 70)["label"] == "overconfident"
    assert ai.calibration_label(50, 80)["label"] == "underconfident"
    assert ai.calibration_label(86, 70)["label"] == "overconfident"  # gap 16
    assert ai.calibration_label(85, 70)["label"] == "well_calibrated"  # gap 15


def test_verify_score_shape():
    out = ai.verify_score({"chapter_score": 88, "reasoning_score": 92, "honeypot_score": 2}, {})
    assert out["status"] in ("agreed", "uncertain")
    assert isinstance(out["note"], str)
