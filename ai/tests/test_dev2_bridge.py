"""DEV 2 bridge compatibility: names backend/app/services/engine.py probes.

The backend wraps the engine with ``getattr(engine, name, None)`` and falls back to a
deterministic stand-in when the attribute is missing. These tests pin the two names it
looks for so the live path can never silently regress to the stand-in.
"""
import ai


def test_score_reasoning_is_exposed_and_bounded():
    assert callable(ai.score_reasoning)
    out = ai.score_reasoning("Because the fiber tree can be interrupted, a long render "
                             "yields to higher-priority work; the trade-off is more bookkeeping.")
    assert isinstance(out, int)
    assert 0 <= out <= 100


def test_score_reasoning_empty_is_bounded():
    assert 0 <= ai.score_reasoning("") <= 100


def test_interview_follow_up_is_exposed():
    assert callable(ai.interview_follow_up)
    out = ai.interview_follow_up({"chapter_id": "ch_01"}, "I think it batches updates.", {})
    assert isinstance(out, str) and out.strip()


def test_interview_follow_up_paste_path():
    out = ai.interview_follow_up({"chapter_id": "ch_01"}, "pasted text", {"paste_detected": True})
    assert isinstance(out, str) and out.strip()


def test_bridge_names_the_backend_probes_all_exist():
    # Exactly the names services/engine.py looks up via getattr(engine, name, None).
    for name in ("score_reasoning", "interview_follow_up", "socratic_ask",
                 "suggest_questions", "start_interview", "classify_honeypot",
                 "pick_honeypot_term", "verify_score", "score_chapter"):
        assert hasattr(ai, name), f"ai.{name} missing — DEV 2 bridge would fall back"
