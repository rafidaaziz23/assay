"""DB field additions owned by DEV 2 (backend-only).

Everything here is additive: no existing field is removed or repurposed, so DEV 1's
frontend bundle and DEV 3's engine keep working unchanged. Each entry documents why
it exists and who reads it.

Why a separate module: the API contract (`docs/architecture/API-CONTRACTS.md`) is the frozen
agreement between the three devs. Fields DEV 2 needs for its own persistence should
not silently mutate that contract, and they should be easy to lift into it once
ACC'd at sync.

Frontend follow-ups (not required for the backend gate — the frontend already falls
back to mocks and its own defaults without any of these):

* ``scenario``       — drive the two cached demo beats from the UI (demo toggle).
* ``engine``         — show a "live vs deterministic" chip.
* ``focus_summary``  — render the integrity log in the report.
* ``calibration``    — show predicted/predicted-gap on the report page.
* ``elective``       — visibly mark items the student unchecked (F2 note).
* ``integrity_score``— explain *why* the score dropped (caught scenario).
* ``cache``          — surface the R7 cache version in the demo-safety badge.
"""

from __future__ import annotations

import re
import uuid
from typing import Any, Dict, List, Tuple


def _id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:6]}"


# ── F2 — checklist ─────────────────────────────────────────────────────────────

def tag_elective(items: List[Dict[str, Any]], selected_ids: List[str]) -> List[Dict[str, Any]]:
    """Add ``elective`` to every checklist item.

    Frontend-compatible addition, not a contract break: PRD section 3 Step 2 says the
    student "boleh uncheck/check item", but nothing in the response marked *what the
    engine proposed* versus *what the student kept*. The UI could not show an unchecked
    item as a deliberate choice without guessing from `selected` alone.

    ``elective`` = the engine proposed the item as selected AND the student dropped it.
    That needs the generation-time default, so items must carry ``proposed_selected``
    (set when the checklist is generated); falling back to the current ``selected``
    would make every dropped item look intentionally-chosen and every item look
    non-elective right after a PUT rewrote the flag.
    """
    wanted = set(selected_ids or [])
    out = []
    for item in items:
        row = dict(item)
        proposed = bool(row.pop("proposed_selected", row.get("selected", True)))
        row["elective"] = proposed and row["item_id"] not in wanted
        out.append(row)
    return out


# ── F14 — calibration ──────────────────────────────────────────────────────────

def calibration_labels(gap: int) -> Tuple[int, str]:
    """Signed gap + label per API-CONTRACTS section 2.6.

    The contract cannot be satisfied literally inside its own schema. The response
    carries ``calibration_gap: int`` — the signed difference, since the whole point is
    to show *direction* (overconfident vs underconfident) — while the report's
    ``summary.mean_calibration_gap`` is an average distance, which is unsigned. Keeping
    both fields named ``..._gap`` with different signs is how the report ends up
    averaging a mix of +28 and -28 into a misleadingly small number.

    Fix that is safe on both sides: the response keeps the signed contract value
    (frontend renders it as-is), the label drives colouring, and the report averages
    ``abs()``. Owned by backend because the report aggregation is (F16).
    """
    gap = int(gap)
    if gap > 15:
        return gap, "overconfident"
    if gap < -15:
        return gap, "underconfident"
    return gap, "well_calibrated"


# ── F9 / F16 — score transparency ──────────────────────────────────────────────

def explain_score_delta(score: Dict[str, Any], integrity_flag: str) -> Dict[str, Any]:
    """Break a chapter score into its named parts.

    DEV 3's engine freezes the formula (ai/core.py: chapter = reasoning + honeypot +
    integrity adjustment). The backend owns integrity events, so only the backend can
    show *why* a score differs from the reasoning score. Needed for the "caught" demo
    beat, where the drop must be explainable on camera.
    """
    from ..core.integrity import INTEGRITY_ADJUSTMENT  # local import: avoids a cycle

    reasoning = int(score.get("reasoning_score", score.get("chapter_score", 0)))
    honeypot = int(score.get("honeypot_score", 0))
    adjustment = INTEGRITY_ADJUSTMENT.get((integrity_flag or "clean").strip(), 0)
    return {
        "reasoning": reasoning,
        "honeypot": honeypot,
        "integrity_adjustment": adjustment,
        "integrity_flag": integrity_flag or "clean",
        "total": int(score.get("chapter_score", reasoning + honeypot + adjustment)),
    }


# ── F11–F13 — integrity ────────────────────────────────────────────────────────

def integrity_score(integrity_flag: str) -> int:
    """Map an integrity flag to the 0-100 dimension used by the chapter score.

    Mirrors the engine's ``INTEGRITY_ADJUSTMENT`` idea on a 0-100 scale so the report can
    show *why* a chapter score dropped ("integrity 97/100") instead of only a flag token.
    ``assisted_unverified`` scores 100 on purpose: Accessible Mode must not read as a
    penalty (PRD risk R6). The flag itself still carries the nuance — the number does not
    replace it.
    """
    from ..core.integrity import INTEGRITY_ADJUSTMENT  # local import: avoids a cycle

    adjustment = INTEGRITY_ADJUSTMENT.get((integrity_flag or "clean").strip(), 0)
    return max(0, min(100, 100 + adjustment))


# ── generic response metadata ──────────────────────────────────────────────────

def scenario_meta(scenario_id: str) -> Dict[str, Any]:
    """Which cached scenario a response came from (F17 two-beat demo)."""
    return {"scenario": scenario_id}


def engine_meta(live: bool) -> Dict[str, Any]:
    """Whether the response came from a live model call or the deterministic path."""
    return {"engine": "live" if live else "deterministic_cache"}


def cache_meta(version: str) -> Dict[str, Any]:
    """R7: expose the cache schema version so a stale cache is visible, not silent."""
    return {"cache": {"schema_version": version}}


# ── PDF ingest (F4) ────────────────────────────────────────────────────────────

_PAGE_MARKER = re.compile(r"^\s*(?:\[?\s*(?:page|halaman|hal\.?)\s*(\d{1,4})\s*\]?)\s*$", re.I)


def page_anchored_text(raw_text: str) -> List[Dict[str, Any]]:
    """Split an uploaded plain-text document into pages when it has page markers.

    F4 requires the ingest to keep page numbers: losing them kills the honeypot's main
    claim ("this term isn't on any page of your module"). A text upload has no real
    page structure, so honour explicit markers and otherwise store one page — inventing
    pages would be worse than admitting there is only one.
    """
    if not raw_text or not raw_text.strip():
        return []
    lines = raw_text.splitlines()
    pages: List[Dict[str, Any]] = []
    current_no = 1
    buffer: List[str] = []
    seen_marker = False

    def flush() -> None:
        text = "\n".join(buffer).strip()
        if text:
            pages.append({"page": current_no, "text": text, "char_count": len(text)})

    for line in lines:
        match = _PAGE_MARKER.match(line)
        if match:
            flush()
            buffer = []
            current_no = int(match.group(1))
            seen_marker = True
            continue
        buffer.append(line)
    flush()

    if not seen_marker:
        # One page, honestly labelled. No fabricated pagination.
        text = raw_text.strip()
        return [{"page": 1, "text": text, "char_count": len(text)}]
    if not pages:
        return [{"page": 1, "text": raw_text.strip(), "char_count": len(raw_text.strip())}]
    return pages


if __name__ == "__main__":  # pragma: no cover - manual shape dump
    import json

    print(json.dumps({
        "page_anchored_text": page_anchored_text("Page 1\nhello\n\nPage 2\nworld"),
        "calibration_labels": calibration_labels(28),
    }, indent=2))
