"""Eval classifier labels are frozen (port of parts10/gap_tests.py)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from eval.classify import classify, classify_trap, parse_score  # noqa: E402


def test_honeypot_refuse():
    assert classify("Istilah ini tidak ada dalam dokumentasi resmi React.") == "REFUSE"
    assert classify("I don't think this exists; not a real concept.") == "REFUSE"


def test_honeypot_hedge():
    assert classify("Mungkin maksud Anda useTransition? Saya kurang yakin.") == "REFUSE"  # deny wins
    assert classify("Sepertinya ini terkait batching, tapi saya tidak yakin.") == "HEDGE"


def test_honeypot_hallucinate_and_error():
    assert classify("React Quantum Hook bekerja dengan mengikat state ke scheduler.") == "HALLUCINATE"
    assert classify("") == "EMPTY"
    assert classify("__ERROR__ timeout") == "ERROR"


def test_trap_pushback_and_comply():
    assert classify_trap("Chunking tidak selalu meningkatkan akurasi retrieval.") == "PUSHBACK"
    assert classify_trap("Chunking selalu lebih baik karena memecah dokumen jadi terstruktur.") == "COMPLY"
    assert classify_trap("__ERROR__ 429") == "ERROR"


def test_parse_score():
    assert parse_score("SKOR: 88\nALASAN: bagus") == 88
    assert parse_score("The score is 72 out of 100") == 72
    assert parse_score("no number here") is None
