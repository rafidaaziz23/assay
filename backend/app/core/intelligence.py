"""Deterministic pre-filter (ADR 002 section 2.1).

The integrity flag is computed from signals the model must not be asked to judge:

* **client telemetry** — a long, articulate answer that arrived in 2 seconds with 900
  keystrokes/minute was not typed. The ADR calls this the deterministic pre-filter and
  it is the only evidence class that is not itself an LLM opinion.
* **Focus Mode events** — see ``core.integrity``.

Order matters: an explicit Focus Mode flag wins over telemetry, because Focus Mode is a
device-side measurement while telemetry is self-reported by the same client being
measured. Accessible Mode (``assisted_unverified``) is never overridden — a student who
cannot run a camera must not be re-flagged by telemetry.
"""
from __future__ import annotations

from typing import Any, Dict, Optional

from .integrity import (
    INTEGRITY_ASSISTED,
    INTEGRITY_ASSISTED_UNVERIFIED,
    INTEGRITY_CLEAN,
)

# Thresholds for the paste heuristic. Deliberately conservative: a fast typist must not
# be flagged, so it takes an implausibly short answer AND an implausible rate.
PASTE_MAX_SECONDS = 3
PASTE_MIN_CPM = 700
PASTE_MIN_WORDS = 40


def telemetry_suggests_paste(telemetry: Optional[Dict[str, Any]], text: str = "") -> bool:
    """True when the typing dynamics are not physically plausible.

    Requires the explicit ``paste_detected`` event, or the combination of an editable
    answer appearing faster than a human can type it. A single signal is enough to be
    suspicious but is reported as a suspicion, not as proof.
    """
    if not telemetry:
        return False
    if telemetry.get("paste_detected"):
        return True
    seconds = int(telemetry.get("duration_seconds") or 0)
    cpm = int(telemetry.get("keystroke_cpm") or 0)
    words = len((text or "").split())
    return seconds <= PASTE_MAX_SECONDS and cpm >= PASTE_MIN_CPM and words >= PASTE_MIN_WORDS


def telemetry_flag(
    paste_seen: bool,
    focus_flag: Optional[str] = None,
    text: str = "",
) -> str:
    """Resolve the final integrity flag from telemetry and Focus Mode."""
    focus_flag = (focus_flag or "").strip()
    if focus_flag == INTEGRITY_ASSISTED_UNVERIFIED:
        # Accessible Mode: unverified rather than clean, and never re-flagged.
        return INTEGRITY_ASSISTED_UNVERIFIED
    if focus_flag == INTEGRITY_ASSISTED:
        return INTEGRITY_ASSISTED
    if paste_seen:
        return INTEGRITY_ASSISTED
    return INTEGRITY_CLEAN
