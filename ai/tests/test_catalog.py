"""The honeypot catalog must stay a valid, auditable 10-term artifact (ADR 005)."""
import json
from pathlib import Path

CATALOG = Path(__file__).resolve().parents[2] / "prompts" / "honeypot-catalog.json"


def _entries():
    data = json.loads(CATALOG.read_text(encoding="utf-8"))
    return data["terms"] if isinstance(data, dict) else data


def test_catalog_has_ten_terms():
    assert len(_entries()) >= 10


def test_every_entry_has_required_fields():
    for e in _entries():
        assert e["term"] and e["category"] and e["trap_type"]
        assert e["expected_action"] == "REJECT_AS_FICTITIOUS"
        assert e["catalog_id"].startswith("hp_")
        assert isinstance(e.get("topic_keywords"), list) and e["topic_keywords"]


def test_terms_and_ids_are_unique():
    terms = [e["term"] for e in _entries()]
    ids = [e["catalog_id"] for e in _entries()]
    assert len(set(terms)) == len(terms)
    assert len(set(ids)) == len(ids)


def test_trap_types_in_known_set():
    allowed = {"fictional_term", "false_premise", "trap_number", "over_claim"}
    for e in _entries():
        assert e["trap_type"] in allowed
